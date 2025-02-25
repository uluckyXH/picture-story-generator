#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Word文档生成器：负责将题目内容转换为Word文档
"""

import os
import logging
from typing import Dict, Any, List, Union
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WordGenerator:
    """Word文档生成器类，负责创建和格式化Word文档"""
    
    def __init__(self, template_path=None):
        """
        初始化Word文档生成器
        
        Args:
            template_path: Word模板文件路径，如果为None则创建新文档
        """
        self.template_path = template_path
        logger.info("初始化Word文档生成器")
    
    def create_document(self, content: List[Dict], output_path: str) -> str:
        """
        创建Word文档
        
        Args:
            content: 文档内容，包含题目信息的列表
            output_path: 输出文件路径
            
        Returns:
            生成的文档路径
        """
        logger.info(f"开始创建Word文档，输出路径: {output_path}")
        
        # 创建文档对象
        if self.template_path and os.path.exists(self.template_path):
            doc = Document(self.template_path)
            logger.info(f"使用模板创建文档: {self.template_path}")
        else:
            doc = Document()
            logger.info("创建新文档")
        
        # 设置文档样式
        self._setup_document_styles(doc)
        
        # 添加文档标题
        self._add_title(doc, "小学二年级语文练习题")
        
        # 收集所有参考答案，按大题分组
        answers = []
        
        # 处理每种题型
        for item in content:
            if "maxTitle" in item and "questions" in item:
                # 添加大题标题
                self._add_section_title(doc, item["maxTitle"])
                
                # 添加题目要求
                if "require" in item:
                    self._add_requirement(doc, item["require"])
                
                # 收集当前大题的答案
                current_answers = {"title": item["maxTitle"], "answers": []}
                
                # 处理题目
                if item["maxTitle"] == "句子仿写练习题":
                    self._add_imitation_questions(doc, item["questions"], current_answers)
                elif item["maxTitle"] == "看图写话练习题":
                    self._add_picture_questions(doc, item["questions"], current_answers)
                
                # 添加到总答案列表
                if current_answers["answers"]:
                    answers.append(current_answers)
        
        # 添加分页符
        doc.add_page_break()
        
        # 添加答案部分
        self._add_answers_section(doc, answers)
        
        # 保存文档
        doc.save(output_path)
        
        logger.info(f"文档创建完成: {output_path}")
        return output_path
    
    def _setup_document_styles(self, doc):
        """设置文档样式"""
        # 设置中文字体
        style_names = ['Normal', 'Heading 1', 'Heading 2', 'Heading 3']
        for style_name in style_names:
            style = doc.styles[style_name]
            font = style.font
            font.name = 'Times New Roman'
            font.size = Pt(12)
            # 设置中文字体
            font._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        
        # 创建自定义样式
        if 'Title' not in doc.styles:
            title_style = doc.styles.add_style('Title', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(18)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(12)
            # 设置中文字体
            title_style.font._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        
        if 'Section' not in doc.styles:
            section_style = doc.styles.add_style('Section', WD_STYLE_TYPE.PARAGRAPH)
            section_style.font.name = 'Times New Roman'
            section_style.font.size = Pt(16)
            section_style.font.bold = True
            section_style.paragraph_format.space_before = Pt(12)
            section_style.paragraph_format.space_after = Pt(8)
            # 设置中文字体
            section_style.font._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        
        if 'Requirement' not in doc.styles:
            req_style = doc.styles.add_style('Requirement', WD_STYLE_TYPE.PARAGRAPH)
            req_style.font.name = 'Times New Roman'
            req_style.font.size = Pt(14)
            req_style.font.italic = True
            req_style.paragraph_format.space_after = Pt(8)
            # 设置中文字体
            req_style.font._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
        
        if 'Question' not in doc.styles:
            q_style = doc.styles.add_style('Question', WD_STYLE_TYPE.PARAGRAPH)
            q_style.font.name = 'Times New Roman'
            q_style.font.size = Pt(12)
            q_style.paragraph_format.space_after = Pt(6)
            q_style.paragraph_format.first_line_indent = Inches(0.25)
            # 设置中文字体
            q_style.font._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        
        if 'Answer' not in doc.styles:
            a_style = doc.styles.add_style('Answer', WD_STYLE_TYPE.PARAGRAPH)
            a_style.font.name = 'Times New Roman'
            a_style.font.size = Pt(12)
            a_style.font.italic = True
            a_style.paragraph_format.space_after = Pt(6)
            a_style.paragraph_format.left_indent = Inches(0.5)
            # 设置中文字体
            a_style.font._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    def _add_title(self, doc, title):
        """添加文档标题"""
        paragraph = doc.add_paragraph(title, style='Title')
        doc.add_paragraph()  # 添加空行
    
    def _add_section_title(self, doc, title):
        """添加大题标题"""
        paragraph = doc.add_paragraph(title, style='Section')
    
    def _add_requirement(self, doc, requirement):
        """添加题目要求"""
        paragraph = doc.add_paragraph(requirement, style='Requirement')
    
    def _add_imitation_questions(self, doc, questions, answers_collector):
        """添加句子仿写题"""
        for question in questions:
            # 添加题号和问题
            q_text = f"{question['number']}. {question['question']}"
            paragraph = doc.add_paragraph(q_text, style='Question')
            
            # 添加仿写空格
            if "Imitate_writing" in question and isinstance(question["Imitate_writing"], list):
                imitate_text = ""
                for i, word in enumerate(question["Imitate_writing"]):
                    if i > 0:
                        # 添加下划线空格
                        imitate_text += "_____________"
                    imitate_text += word
                
                # 最后一个词后也添加下划线
                imitate_text += "_____________"
                
                p = doc.add_paragraph(style='Normal')
                p.paragraph_format.left_indent = Inches(0.5)
                p.add_run(imitate_text)
            
            # 收集参考答案
            if "reference_answer" in question:
                answers_collector["answers"].append({
                    "number": question["number"],
                    "question": question["question"],
                    "answer": question["reference_answer"]
                })
            
            # 添加空行
            doc.add_paragraph()
    
    def _add_picture_questions(self, doc, questions, answers_collector):
        """添加看图写话题"""
        for question in questions:
            # 添加题号和问题
            q_text = f"{question['number']}. {question['question']}"
            paragraph = doc.add_paragraph(q_text, style='Question')
            
            # 添加图片描述（提示词）
            if "prompt" in question:
                p = doc.add_paragraph(style='Normal')
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.right_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(0.25)
                p.add_run(f"图片描述：{question['prompt']}").italic = True
            
            # 添加写作空间
            p = doc.add_paragraph(style='Normal')
            p.paragraph_format.left_indent = Inches(0.5)
            p.add_run("写话：").bold = True
            
            # 添加多行空白供学生写作
            for i in range(8):
                doc.add_paragraph("_" * 60, style='Normal')
                # 在循环最后一次加上句号
                if i == 7:
                    doc.add_paragraph("。", style='Normal')
            
            # 收集参考答案
            if "reference_answer" in question:
                answers_collector["answers"].append({
                    "number": question["number"],
                    "question": question["question"],
                    "answer": question["reference_answer"]
                })
            
            # 添加空行
            doc.add_paragraph()
    
    def _add_answers_section(self, doc, answers):
        """添加答案部分"""
        # 添加答案标题
        self._add_title(doc, "参考答案")
        
        # 处理每种题型的答案
        for answer_group in answers:
            # 添加大题标题
            self._add_section_title(doc, f"{answer_group['title']}参考答案")
            
            # 添加每道题的答案
            for answer_item in answer_group["answers"]:
                # 添加题号和问题
                q_text = f"{answer_item['number']}. {answer_item['question']}"
                paragraph = doc.add_paragraph(q_text, style='Question')
                
                # 添加参考答案
                p = doc.add_paragraph(style='Answer')
                run = p.add_run(f"参考答案：{answer_item['answer']}")
                run.italic = True
            
            # 在不同大题之间添加空行
            doc.add_paragraph()


def main():
    """测试函数"""
    # 简单的测试数据
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
                }
            ]
        }
    ]
    
    # 创建Word文档
    generator = WordGenerator()
    output_path = "test_exercises.docx"
    generator.create_document(test_content, output_path)
    print(f"测试文档已创建: {output_path}")


if __name__ == "__main__":
    main() 