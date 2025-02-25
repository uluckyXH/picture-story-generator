#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
import requests
import datetime
import re
import time
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


def generate_image(prompt: str,
                  api_key: str,
                  base_url: str,
                  model_name: str = "dall-e-3",
                  model_type: str = "openai",
                  size: str = "768x768",
                  n: int = 1,
                  output_dir: str = None) -> Tuple[Optional[str], Optional[Dict], str, Optional[str]]:
    """
    生成图像并返回图像URL
    
    Args:
        prompt: 图像生成提示词
        api_key: API密钥
        base_url: API基础URL
        model_name: 模型名称，默认为"dall-e-3"
        model_type: 模型类型，默认为"openai"
        size: 图像尺寸，默认为"768x768"
        n: 生成图像数量，默认为1
        output_dir: 保存图像的目录，如果提供则会将图像保存到该目录
        
    Returns:
        包含图像URL、完整响应数据和错误信息（如果有）的元组
    """
    logger.info(f"开始生成图像，使用模型: {model_name}, 提示词长度: {len(prompt)}")
    
    image_url = None
    response_data = None
    error_msg = ""
    local_image_path = None
    
    # 根据不同的模型类型调用不同的API
    if model_type == "openai":
        try:
            # 构建请求数据
            data = {
                "prompt": prompt,
                "n": n,
                "model": model_name,
                "size": size
            }
            
            # 发送请求
            response = requests.post(
                f"{base_url}/images/generations",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 从响应中提取图像URL
                if "data" in response_data and len(response_data["data"]) > 0:
                    if "url" in response_data["data"][0]:
                        image_url = response_data["data"][0]["url"]
                        logger.info(f"成功获取图像URL: {image_url[:50]}...")
                        
                        # 如果提供了输出目录，则下载并保存图像
                        if output_dir and image_url:
                            try:
                                # 下载图像
                                img_response = requests.get(image_url, timeout=30)
                                if img_response.status_code == 200:
                                    # 生成图像文件名
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    image_filename = f"image_{timestamp}.png"
                                    local_image_path = os.path.join(output_dir, image_filename)
                                    
                                    # 保存图像
                                    with open(local_image_path, "wb") as img_file:
                                        img_file.write(img_response.content)
                                    
                                    logger.info(f"图像已保存到本地: {local_image_path}")
                                else:
                                    logger.error(f"下载图像失败，状态码: {img_response.status_code}")
                            except Exception as e:
                                logger.error(f"保存图像时发生错误: {str(e)}")
                    else:
                        error_msg = "响应格式异常：未找到url字段"
                else:
                    error_msg = "响应格式异常：未找到data字段或data为空"
            else:
                error_msg = f"API调用失败: {response.status_code}, {response.text}"
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"调用图像生成API时发生错误: {str(e)}"
            logger.exception(error_msg)
    
    # 可以在这里添加其他模型类型的支持
    # elif model_type == "stability":
    #     # 实现Stability AI的API调用
    #     pass
    
    else:
        error_msg = f"未实现的图像生成模型类型: {model_type}"
        logger.warning(error_msg)
    
    # 保存响应数据到JSON文件
    if response_data:
        # 确定保存目录
        if output_dir:
            data_dir = output_dir
        else:
            # 使用默认的data目录
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"创建数据目录: {data_dir}")
        
        # 生成时间戳文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file_path = os.path.join(data_dir, f"image_response_{timestamp}.json")
        
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(response_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"图像生成响应数据已保存到: {json_file_path}")
    
    return image_url, response_data, error_msg, local_image_path


def process_exercises_with_images(
    api_key: str,
    base_url: str,
    model_name: str,
    model_type: str,
    image_api_key: str,
    image_base_url: str,
    imitation_count: int = 2,
    picture_count: int = 1,
    user_requirements: str = "无其它要求",
    temperature: float = 0.7,
    image_model: str = "dall-e-3",
    image_model_type: str = "openai",
    image_size: str = "768x768",
    image_delay: float = 2.0
) -> Tuple[str, Optional[Union[List, Dict]]]:
    """
    处理整个练习生成流程，包括生成题目、生成图片和创建Word文档
    
    Args:
        api_key: 模型API密钥
        base_url: 模型API基础URL
        model_name: 模型名称
        model_type: 模型类型
        image_api_key: 图片生成API密钥
        image_base_url: 图片生成API基础URL
        imitation_count: 句子仿写题数量，默认为2
        picture_count: 看图写话题数量，默认为1
        user_requirements: 用户要求，默认为"无其它要求"
        temperature: 模型温度参数，默认为0.7
        image_model: 图像生成模型，默认为"dall-e-3"
        image_model_type: 图像生成模型类型，默认为"openai"
        image_size: 图像尺寸，默认为"768x768"
        image_delay: 图像生成请求之间的延迟时间（秒），默认为2.0秒
        
    Returns:
        输出目录路径和处理后的数据的元组
    """
    logger.info(f"开始处理练习生成流程，句子仿写题数量: {imitation_count}, 看图写话题数量: {picture_count}")
    
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
2、按结构生成{imitation_count}个句子仿写练习题
2、首先先生成仿写题目的例句
3、生成例句和参考答案后，根据以下要求来生成仿写引导：
 - 在题目对象中增加Imitate_writing数组字段
 - 把参考答案去掉多个空，例如参考答案为"小兔子在草地上跑来跑去"，去空后："小兔子在（）上（）"
 - 然后把剩下的文字按顺序放入Imitate_writing数组中，数组例子：["小兔子在","","上",""]
4、注意不要以例子来生成题目，要保证题目的多样性，例子只是给你作为格式的理解和参考，不要把参考答案分割放入Imitate_writing中，而是将参考答案按例子去除留空后，将剩余的文字按顺序放入数组
5、仿写引导例子只做格式参考，不做生成题目参考

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
        temperature=temperature
    )
    
    if content is None:
        logger.error(f"获取模型响应失败: {error}")
        print(f"生成题目失败: {error}")
        return None, None
    
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
        print(f"生成题目失败: 无法提取有效的JSON数据")
        return None, None
    
    # 创建输出目录
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
    
    # 保存原始JSON数据到时间戳目录
    json_file_path = os.path.join(output_dir, "exercises.json")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(exercises_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"原始题目数据已保存到: {json_file_path}")
    
    # 为看图写话题目生成图片
    logger.info("开始为看图写话题目生成图片")
    
    # 查找看图写话练习题
    for item in exercises_data:
        if isinstance(item, dict) and item.get("maxTitle") == "看图写话练习题":
            questions = item.get("questions", [])
            for i, question in enumerate(questions):
                if "prompt" in question:
                    # 使用prompt作为图片生成提示词
                    prompt = question["prompt"]
                    logger.info(f"为题目 {question.get('number')} 生成图片，提示词长度: {len(prompt)}")
                    
                    # 添加延迟，避免频繁请求
                    if i > 0 and image_delay > 0:
                        logger.info(f"等待 {image_delay} 秒后继续生成下一张图片...")
                        time.sleep(image_delay)
                    
                    # 调用图片生成API，使用单独的图片API配置
                    image_url, response_data, error, local_image_path = generate_image(
                        prompt=prompt,
                        api_key=image_api_key,
                        base_url=image_base_url,
                        model_name=image_model,
                        model_type=image_model_type,
                        size=image_size,
                        output_dir=output_dir
                    )
                    
                    if image_url:
                        # 将图片URL添加到题目数据中
                        question["image_url"] = image_url
                        # 如果有本地图片路径，也添加到题目数据中
                        if local_image_path:
                            question["local_image_path"] = local_image_path
                        logger.info(f"成功为题目 {question.get('number')} 生成图片")
                    else:
                        logger.error(f"为题目 {question.get('number')} 生成图片失败: {error}")
                        print(f"为题目 {question.get('number')} 生成图片失败: {error}")
    
    # 更新JSON数据（包含图片URL和本地路径）
    updated_json_file_path = os.path.join(output_dir, "exercises_with_images.json")
    with open(updated_json_file_path, "w", encoding="utf-8") as f:
        json.dump(exercises_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"带图片URL的题目数据已保存到: {updated_json_file_path}")
    
    # 生成Word文档
    try:
        word_generator = WordGenerator()
        word_file_path = os.path.join(output_dir, "exercises.docx")
        word_generator.create_document(exercises_data, word_file_path)
        logger.info(f"Word文档已生成: {word_file_path}")
    except Exception as e:
        logger.error(f"生成Word文档时发生错误: {str(e)}")
        print(f"生成Word文档时发生错误: {str(e)}")
    
    return output_dir, exercises_data


def generate_exercises(exercises_data: Union[List, Dict]) -> Tuple[str, Optional[Union[List, Dict]]]:
    """
    处理题目数据并保存到文件
    
    Args:
        exercises_data: 题目数据，通常是从模型响应中提取的JSON数据
        
    Returns:
        保存的目录路径和处理后的JSON数据的元组
    """
    logger.info(f"开始处理题目数据")
    
    if exercises_data is None:
        logger.error("题目数据为空")
        return "题目数据为空", None
    
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
        print(f"生成Word文档时发生错误: {str(e)}")
    
    return output_dir, exercises_data

def main():
    """主函数"""
    # 配置参数
    api_key = ""  # 模型API密钥
    base_url = "https://api.siliconflow.cn/v1"  # 模型API基础URL
    model_name = "deepseek-ai/DeepSeek-V3"  # 模型名称
    model_type = "openai"  # 模型类型
    
    # 图片生成API配置
    image_api_key = ""  # 图片生成API密钥
    image_base_url = "https://api.openai.com/v1"  # 图片生成API基础URL
    image_model = "dall-e-3"  # 图片生成模型
    image_size = "1024x1024"  # 图片尺寸
    image_model_type = "openai"  # 图片生成模型类型
    image_delay = 2.0  # 图片生成请求之间的延迟时间（秒）
    
    # 题目生成参数
    imitation_count = 2  # 句子仿写题数量
    picture_count = 2  # 看图写话题数量
    user_requirements = "无其它要求"  # 用户要求
    
    # 调用处理流程
    output_dir, processed_data = process_exercises_with_images(
        api_key=api_key, # 模型API密钥
        base_url=base_url, # 模型API基础URL
        model_name=model_name, # 模型名称
        model_type=model_type, # 模型类型
        image_api_key=image_api_key, # 图片生成API密钥
        image_base_url=image_base_url, # 图片生成API基础URL
        imitation_count=imitation_count, # 句子仿写题数量
        picture_count=picture_count, # 看图写话题数量
        user_requirements=user_requirements, # 用户要求
        image_model=image_model, # 图片生成模型
        image_model_type=image_model_type, # 图片生成模型类型
        image_size=image_size, # 图片尺寸
        image_delay=image_delay # 图片生成请求之间的延迟时间
    )
    
    if output_dir and processed_data:
        print(f"题目数据已保存到目录: {output_dir}")
        
        # 检查Word文档是否生成成功
        word_file_path = os.path.join(output_dir, "exercises.docx")
        if os.path.exists(word_file_path):
            print(f"Word文档已生成: {word_file_path}")
        else:
            print("Word文档生成失败，请查看错误日志")
        
        print(f"生成的题目数量: {sum(len(item.get('questions', [])) for item in processed_data if isinstance(item, dict))}")
    else:
        print("生成题目失败")


if __name__ == "__main__":
    main()