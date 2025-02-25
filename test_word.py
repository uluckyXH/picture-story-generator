#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Word文档生成功能
"""

import os
import json
from word_generator import WordGenerator

def main():
    """测试Word文档生成功能"""
    print("开始测试Word文档生成功能...")
    
    # 测试数据
    test_content = [
        {
            "maxTitle": "句子仿写练习题",
            "require": "请根据例句仿写句子。",
            "questions": [
                {
                    "number": 1,
                    "question": "例句：小鸟在树上唱歌。",
                    "reference_answer": "小鱼在水里游来游去。",
                    "Imitate_writing": ["小鱼", "在", "里"]
                },
                {
                    "number": 2,
                    "question": "例句：小朋友在操场上跑步。",
                    "reference_answer": "小猫咪在沙发上打盹。",
                    "Imitate_writing": ["小猫咪", "在", "上"]
                }
            ]
        },
        {
            "maxTitle": "看图写话练习题",
            "require": "请根据图片提示写一段话。",
            "questions": [
                {
                    "number": 1,
                    "question": "图片里有哪些动物？它们在做什么？",
                    "prompt": "图片中有一只大熊猫和一只小熊猫在竹林里玩耍。大熊猫正在吃竹子，小熊猫则好奇地四处张望。竹林里还有几只小鸟在树枝上唱歌。",
                    "reference_answer": "图片中有一只大熊猫和一只小熊猫在竹林里玩耍。大熊猫正在吃竹子，小熊猫则好奇地四处张望。竹林里还有几只小鸟在树枝上唱歌。"
                },
                {
                    "number": 2,
                    "question": "图片里的小朋友在做什么？他们的表情如何？",
                    "prompt": "图片中有三个小朋友在公园里放风筝。一个小男孩正在跑着放风筝，另外两个小女孩则站在旁边笑着看。天空中还有几只彩色风筝在飞舞。",
                    "reference_answer": "图片中有三个小朋友在公园里放风筝。一个小男孩正在跑着放风筝，另外两个小女孩则站在旁边笑着看。他们的脸上都洋溢着快乐的笑容。天空中还有几只彩色风筝在飞舞，非常美丽。"
                }
            ]
        }
    ]
    
    # 保存测试数据为JSON文件
    if not os.path.exists("test_data"):
        os.makedirs("test_data")
    
    json_path = os.path.join("test_data", "test_exercises.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_content, f, ensure_ascii=False, indent=4)
    
    print(f"测试数据已保存到: {json_path}")
    
    # 创建Word文档
    generator = WordGenerator()
    output_path = os.path.join("test_data", "test_exercises.docx")
    
    try:
        generator.create_document(test_content, output_path)
        print(f"测试文档已成功创建: {output_path}")
        print("测试成功！")
        print("注意：参考答案已移至文档最后一页")
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    main() 