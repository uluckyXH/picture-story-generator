#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
import requests
import datetime
import re
from typing import Dict, Any, List, Optional, Union, Tuple

# 导入Word生成模块
from word_generator import WordGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 模型调用方法，支持不同的模型类型，直接返回模型响应内容
def call_model(context: List[Dict[str, str]], 
               api_key: str,
               base_url: str,
               model_name: str,
               model_type: str,
               temperature: float = 0.7) -> Tuple[Optional[str], str]:
    """
    调用大模型API获取响应内容
    
    Args:
        context: 对话上下文，包含历史消息
        api_key: API密钥
        base_url: API基础URL
        model_name: 模型名称
        model_type: 模型类型
        temperature: 模型温度参数，控制随机性，默认0.7
        
    Returns:
        模型响应内容和错误信息（如果有）的元组
    """
    logger.info(f"调用模型: {model_name}")
    
    # 根据不同的模型类型调用不同的API
    if model_type == "openai":
        try:
            # 构建请求数据
            data = {
                "model": model_name,
                "messages": context,
                "temperature": temperature,
                "top_p": 1
            }
            
            # 发送请求
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 从OpenAI响应中提取内容
                if "choices" in result and len(result["choices"]) > 0:
                    if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                        content = result["choices"][0]["message"]["content"]
                        logger.info(f"成功获取OpenAI响应，内容长度: {len(content)}")
                        return content, ""
                    else:
                        return None, "OpenAI响应格式异常：未找到message.content字段"
                else:
                    return None, "OpenAI响应格式异常：未找到choices字段或choices为空"
            else:
                error_msg = f"API调用失败: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"调用OpenAI模型时发生错误: {str(e)}"
            logger.exception(error_msg)
            return None, error_msg
        
    # 自己增加其它返回格式模型
    else:
        error_msg = f"未实现的模型类型: {model_type}"
        logger.warning(error_msg)
        return None, error_msg


def generate_exercises(api_key: str, 
                       base_url: str, 
                       model_name: str, 
                       model_type: str,
                       imitation_count: int = 3,
                       picture_count: int = 3,
                       user_requirements: str = "无其它要求") -> Tuple[str, Optional[Union[List, Dict]]]:
    """
    生成题目数据并保存到文件
    
    Args:
        api_key: API密钥
        base_url: API基础URL
        model_name: 模型名称
        model_type: 模型类型
        imitation_count: 句子仿写题的数量，默认为3
        picture_count: 看图写话题的数量，默认为3
        user_requirements: 用户的特殊要求，默认为"无其它要求"
        
    Returns:
        保存的目录路径和提取的JSON数据的元组
    """
    logger.info(f"开始生成题目，句子仿写题数量: {imitation_count}, 看图写话题数量: {picture_count}")
    
    # 系统提示词
    system_prompt = """## 角色：题目生成专家擅长生成小学二年级句子仿写和看图写话练习题
## 注意：如果用户有要求，请按用户提供的的要求生成题目，用户的要求只针对题目而不针对格式

## 格式要求：
2、请以纯JSON的形式进行回复，拒绝使用任何markdown语法和出现其它文字
2、首先格式为数组，第一个对象为句子仿写练习题，第二个对象为生成看图写话练习题
3、对象里包含了题目的大题标题，字段名为maxTitle
4、对象里还包含了题目要求字段，字段名为require
5、接着是题目数组的基本结构，数组里包含多个题目对象，每个题目对象包含以下基础字段：
 - 序号，number
 - 问题，question
 - 参考答案，reference_answer
6、所有JSON字段必须为英文，题目都为中文

### 步骤一：生成句子仿写练习题
2、按结构生成{{number}}个句子仿写练习题
2、首先先生成仿写题目的例句
3、生成例句和参考答案后，根据以下要求来生成仿写引导：
 - 在题目对象中增加Imitate_writing数组字段
 - 把参考答案去掉多个空，例如参考答案为”小兔子在草地上跑来跑去“，去空后：”小兔子在（）上（）“
 - 然后把剩下的文字按顺序放入Imitate_writing数组中，数组例子：["小兔子在","","上",""]
4、注意不要以例子来生成题目，要保证题目的多样性，例子只是给你作为格式的理解和参考，不要把参考答案分割放入Imitate_writing中，而是将参考答案按例子去除留空后，将剩余的文字按顺序放入数组

### 步骤二：生成看图写话练习题
2、首先按结构生成{picture_count}个看图写话练习题
2、在看图写话练习题对象中的题目数组增加字段，prompt提示词字段
3、提示词为图片的描述，要符合场景，要描述详细，细节都要描述出来，包括细节、场景、动作，等等，图片提示词风格为卡通风格
4、问题要根据提示词的描述来进行提问"""
    

    # 用户提示词
    user_prompt = f"题目要求：{user_requirements}"
    
    # 构建上下文
    context = [
        {"role": "system", "content": system_prompt.format(imitation_count=imitation_count, picture_count=picture_count)},
        {"role": "user", "content": user_prompt}
    ]
    
    # 调用模型获取原始响应内容
    content, error = call_model(
        context=context,
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        model_type=model_type,
        temperature=0.7
    )
    
    if content is None:
        logger.error(f"获取模型响应失败: {error}")
        
        # 创建错误文件
        error_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_response.txt")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(error)
        
        return f"生成题目失败: {error}。错误详情已保存到: {error_file}", None
    
    # 尝试从响应中提取JSON数据
    exercises_data = None
    
    # 尝试直接解析整个响应
    try:
        exercises_data = json.loads(content)
        logger.info("成功直接解析响应为JSON")
    except json.JSONDecodeError:
        logger.info("直接解析失败，尝试其他提取方法")
        
        # 尝试提取被反引号包围的JSON (```json ... ```)
        json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(json_pattern, content)
        
        if matches:
            logger.info(f"找到{len(matches)}个被反引号包围的JSON块")
            for match in matches:
                try:
                    exercises_data = json.loads(match.strip())
                    logger.info("成功解析被反引号包围的JSON块")
                    break
                except json.JSONDecodeError:
                    continue
        
        # 如果还是没有找到，尝试查找可能的JSON数组
        if exercises_data is None:
            array_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if array_match:
                try:
                    exercises_data = json.loads(array_match.group(0))
                    logger.info("成功提取并解析JSON数组")
                except json.JSONDecodeError:
                    logger.warning("找到可能的JSON数组但解析失败")
    
    # 如果无法提取JSON数据
    if exercises_data is None:
        logger.error("无法从模型响应中提取有效的JSON数据")
        
        # 保存原始响应以便调试
        error_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_response.txt")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"生成题目失败: 无法提取有效的JSON数据。原始响应已保存到: {error_file}", None
    
    # 确保data目录存在
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"创建数据目录: {data_dir}")
    
    # 生成时间戳目录名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(data_dir, timestamp)
    
    # 创建时间戳目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"创建输出目录: {output_dir}")
    
    # 保存JSON数据到时间戳目录
    json_file_path = os.path.join(output_dir, "exercises.json")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(exercises_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"题目数据已保存到: {json_file_path}")
    
    # 生成Word文档
    try:
        word_generator = WordGenerator()
        word_file_path = os.path.join(output_dir, "exercises.docx")
        word_generator.create_document(exercises_data, word_file_path)
        logger.info(f"Word文档已生成: {word_file_path}")
    except Exception as e:
        logger.error(f"生成Word文档时发生错误: {str(e)}")
        # 保存错误信息到文件
        error_file = os.path.join(output_dir, "word_error.txt")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(f"生成Word文档时发生错误: {str(e)}")
        logger.info(f"错误信息已保存到: {error_file}")
    
    return output_dir, exercises_data


def main():
    """主函数"""
    # 从环境变量获取API密钥
    api_key = ""
    
    # 生成题目示例
    output_dir, exercises_data = generate_exercises(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1",
        model_name="deepseek-ai/DeepSeek-V3",
        model_type="openai",
        imitation_count=2,
        picture_count=1
    )
    
    print(f"题目数据已保存到目录: {output_dir}")
    
    # 检查Word文档是否生成成功
    word_file_path = os.path.join(output_dir, "exercises.docx")
    if os.path.exists(word_file_path):
        print(f"Word文档已生成: {word_file_path}")
    else:
        print("Word文档生成失败，请查看错误日志")
    
    if exercises_data:
        print(f"生成的题目数量: {sum(len(item.get('questions', [])) for item in exercises_data if isinstance(item, dict))}")


if __name__ == "__main__":
    main()