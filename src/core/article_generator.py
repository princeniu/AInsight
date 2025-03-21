#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文章生成模块

使用GPT-4o生成高质量AI文章。
"""

import os
import logging
import json
import time
from typing import Dict, Any, Optional, List
import openai
from openai import OpenAI
from tqdm import tqdm
import colorama
from colorama import Fore, Style
import random  # 添加random模块导入

# 初始化colorama
colorama.init()

# 记录最近使用的风格索引，使用一个列表来存储
# 默认记录最近3种风格，如果风格总数少于3，则记录所有风格
RECENT_USED_STYLES: List[int] = []
# 最大记录的历史风格数量
MAX_STYLE_HISTORY = 3

# 导入配置
try:
    from config.config import OPENAI_API_KEY, MODEL_CONFIG
    logger = logging.getLogger(__name__)
    logger.info("已从config.py加载API密钥和模型配置")
    # 获取默认模型
    DEFAULT_MODEL = MODEL_CONFIG.get("default_model", "gpt-4o")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("未找到config.py文件，尝试从环境变量加载API密钥")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    DEFAULT_MODEL = "gpt-4o"  # 默认模型
    if not OPENAI_API_KEY:
        logger.warning("未设置OPENAI_API_KEY环境变量，请创建config.py文件或设置环境变量")

# 创建OpenAI客户端
# 修复proxies参数问题
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except TypeError as e:
    if "unexpected keyword argument 'proxies'" in str(e):
        logger.warning("检测到OpenAI库版本与proxies参数不兼容，尝试不使用代理初始化客户端")
        # 尝试不使用代理初始化
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        raise

# 文章生成提示模板 - 基础模板
ARTICLE_PROMPT_TEMPLATE_BASE = """
你是一位专业的AI领域科技记者，需要根据以下新闻信息撰写一篇文章。

新闻标题: {title}
新闻摘要: {summary}
新闻链接: {link}
发布日期: {published_date}

{style_instructions}

请直接输出完整的文章内容，不需要包含任何额外的说明。确保文章风格符合要求，能够吸引大量阅读和分享。
"""

# 定义多种文章风格
ARTICLE_STYLES = [
    # 风格1: 今日头条爆款风格
    """
请按照以下要求撰写一篇今日头条平台的爆款文章:

1. 文章结构:
   - 标题：使用爆款标题公式，如"震惊！"、"重磅！"、"突发！"等开头，或使用数字清单、悬念设问、对比反差等吸引眼球的形式, 不要用力过猛形成过于夸张的标题党
   - 开头：第一段必须直击痛点或制造悬念，用简短有力的语句吸引读者继续阅读
   - 正文：使用"爆"、"绝了"、"太厉害了"等情绪化表达，增加共鸣和传播性
   - 分段：每段不超过3句话，大量使用短句，提高可读性
   - 小标题：使用吸引人的小标题分隔内容，如"没想到！"、"太震撼了！"等
   - 结尾：设置悬念或引导读者评论，增加互动性

2. 文章风格:
   - 长度：800-1200字
   - 语气：亲切、口语化，像朋友间聊天
   - 排版：使用加粗、分隔符等突出重点内容
   - 互动性：设置3-5个引导读者思考或评论的问题
   - 话题标签：在文章末尾添加3-5个热门话题标签，如"#AI革命# #科技前沿# #数字未来#", 请根据文章的内容生成热门标签，标签格式：#标签1# #标签2# #标签3#

3. 内容要求:
   - 使用"独家揭秘"、"内部消息"等词语增加稀缺性
   - 添加1-2个虚构的"知情人士"或"行业专家"的爆料或观点
   - 将复杂的AI概念比喻成日常生活中的简单事物
   - 强调新闻对普通人生活的直接影响
   - 加入1-2个与主题相关的热点话题或流行梗
   - 使用"有人说..."、"据了解..."等模糊表达增加神秘感

4. 爆款要素:
   - 制造信息差：暗示你知道一些读者不知道的内幕
   - 情绪共鸣：引发读者的好奇、惊讶、担忧或兴奋等情绪
   - 价值感：强调阅读文章能获得的实用信息或独特见解
   - 争议性：适当加入一些有争议的观点，引发讨论
   - 时效性：强调新闻的紧迫性和重要性
   - 故事性：将枯燥的技术新闻转化为有趣的故事
""",

    # 风格2: 知乎专业分析风格
    """
请按照以下要求撰写一篇知乎平台的专业分析文章:

1. 文章结构:
   - 标题：使用"深度分析"、"全面解读"、"X个角度看"等专业表述
   - 开头：简明扼要地概述新闻背景和核心要点
   - 正文：分为3-5个明确的部分，每部分深入分析一个方面
   - 分段：逻辑清晰，段落之间有明确的过渡
   - 小标题：使用客观、专业的小标题，如"技术原理"、"市场影响"、"未来展望"等
   - 结尾：总结观点并提出前瞻性思考

2. 文章风格:
   - 长度：1200-1800字
   - 语气：专业、客观、理性
   - 排版：使用引用、列表等形式增强可读性
   - 论证：提供数据、案例和逻辑推理支持观点
   - 参考：适当引用行业报告或专家观点增加可信度
   - 话题标签：在文章末尾添加3-5个热门话题标签，如"#AI革命# #科技前沿# #数字未来#", 请根据文章的内容生成热门标签，标签格式：#标签1# #标签2# #标签3#

3. 内容要求:
   - 避免过度情绪化表达，保持客观分析
   - 提供多角度思考，不偏向单一立场
   - 解释技术原理时深入浅出，但不失专业性
   - 分析技术对行业、市场和社会的影响
   - 对比类似技术或产品，突出特点和差异
   - 指出潜在的问题、挑战和局限性

4. 专业要素:
   - 术语准确：正确使用AI领域的专业术语
   - 背景补充：提供必要的背景知识和发展脉络
   - 深度思考：超越表面现象，探讨深层次影响
   - 前瞻视角：分析技术未来可能的发展方向
   - 实用价值：提供读者可以实际应用的见解
   - 理性批判：在肯定成就的同时不回避问题
""",

    # 风格3: 微信公众号科普风格
    """
请按照以下要求撰写一篇微信公众号的科普文章:

1. 文章结构:
   - 标题：简洁明了，使用"一文读懂"、"科普"、"你需要知道的"等表述
   - 开头：以一个有趣的问题或生活场景引入话题
   - 正文：由浅入深，循序渐进地解释概念和原理
   - 分段：段落简短清晰，每个段落聚焦一个要点
   - 小标题：使用问答式或概念式小标题，如"什么是X?"、"X的工作原理"等
   - 结尾：总结要点并展望未来应用

2. 文章风格:
   - 长度：1000-1500字
   - 语气：友好、平易近人，像老师讲课
   - 排版：使用图文并茂的形式，插入表情符号增加亲和力
   - 解释：使用类比和比喻解释复杂概念
   - 互动：适当设置思考问题，增加读者参与感
   - 话题标签：在文章末尾添加3-5个热门话题标签，如"#AI革命# #科技前沿# #数字未来#", 请根据文章的内容生成热门标签，标签格式：#标签1# #标签2# #标签3#
3. 内容要求:
   - 从零基础读者角度出发，避免假设读者已有专业知识
   - 将复杂技术概念转化为日常生活中的类比
   - 解释术语时给出通俗易懂的定义
   - 强调技术在日常生活中的实际应用
   - 澄清常见的误解和疑问
   - 提供进一步学习的资源和建议

4. 科普要素:
   - 准确性：确保科学和技术信息的准确性
   - 趣味性：通过故事、案例和趣闻增加阅读乐趣
   - 实用性：读者阅读后能获得实用知识
   - 启发性：激发读者对科技的兴趣和思考
   - 通俗性：复杂概念简单化，专业术语通俗化
   - 时代性：结合当下热点，增强时代感和共鸣
""",

    # 风格4: 商业分析报告风格
    """
请按照以下要求撰写一篇商业分析报告风格的文章:

1. 文章结构:
   - 标题：简洁专业，包含关键技术和商业价值
   - 摘要：在开头提供200字以内的执行摘要，概述关键点
   - 正文：分为市场分析、技术评估、商业影响、风险分析等部分
   - 分段：每个部分有明确的小标题和结构化内容
   - 数据支持：适当引用市场数据、增长预测等量化信息
   - 结论：提供明确的商业洞见和战略建议

2. 文章风格:
   - 长度：1200-1800字
   - 语气：专业、客观、分析性强
   - 排版：使用要点列表、表格等商业报告常用格式
   - 论证：基于数据和市场趋势进行分析
   - 视角：从投资者、企业决策者的角度评估价值
   - 话题标签：在文章末尾添加3-5个热门话题标签，如"#AI革命# #科技前沿# #数字未来#", 请根据文章的内容生成热门标签，标签格式：#标签1# #标签2# #标签3#

3. 内容要求:
   - 分析技术创新对市场格局的影响
   - 评估技术的商业可行性和盈利模式
   - 分析潜在的市场规模和增长预期
   - 识别主要竞争对手和市场差异化因素
   - 讨论实施过程中可能面临的挑战
   - 提供基于SWOT分析的战略建议

4. 商业要素:
   - 市场洞察：揭示市场趋势和机会
   - 竞争分析：评估竞争格局和差异化策略
   - 价值主张：明确技术的独特价值和优势
   - 风险评估：识别潜在风险和缓解策略
   - 投资视角：分析投资价值和回报预期
   - 行动建议：提供具体可行的下一步行动
"""
]

def print_status(message, status="信息", color=Fore.BLUE):
    """
    打印带颜色的状态信息
    
    Args:
        message: 要显示的消息
        status: 状态文本
        color: 颜色代码
    """
    timestamp = time.strftime("%H:%M:%S")
    status_text = f"{color}[{status}]{Style.RESET_ALL}"
    print(f"[{timestamp}] {status_text} {message}")


def generate_article(news: Dict[str, Any], model: str = None, max_retries: int = 3, verbose: bool = False, 
                    specific_style: int = None) -> Optional[str]:
    """
    使用OpenAI模型生成文章
    
    Args:
        news: 新闻信息，包含title, summary, link, published_date
        model: 要使用的模型名称，如果为None则使用默认模型
        max_retries: 最大重试次数
        verbose: 是否显示详细进度
        specific_style: 指定使用的风格索引（从1开始），如果为None则自动选择
        
    Returns:
        生成的文章内容，如果生成失败则返回None
    """
    global RECENT_USED_STYLES  # 声明使用全局变量
    
    if not OPENAI_API_KEY:
        if verbose:
            print_status("未设置API密钥，请在config.py中设置OPENAI_API_KEY", "错误", Fore.RED)
        logger.error("未设置API密钥，请在config.py中设置OPENAI_API_KEY")
        return None
    
    # 如果未指定模型，使用默认模型
    if model is None:
        model = DEFAULT_MODEL
    
    total_styles = len(ARTICLE_STYLES)
    
    # 如果指定了特定风格
    if specific_style is not None:
        # 将用户输入的1-based索引转换为0-based
        style_index = specific_style - 1
        
        # 检查索引是否有效
        if style_index < 0 or style_index >= total_styles:
            if verbose:
                print_status(f"指定的风格索引 {specific_style} 无效，有效范围: 1-{total_styles}", "错误", Fore.RED)
            logger.error(f"指定的风格索引 {specific_style} 无效，有效范围: 1-{total_styles}")
            # 回退到自动选择
            specific_style = None
        else:
            if verbose:
                print_status(f"使用指定的文章风格 {specific_style}", "风格", Fore.CYAN)
            logger.info(f"使用指定的文章风格 {specific_style}")
    
    # 如果没有指定特定风格或指定的风格无效，则自动选择
    if specific_style is None:
        # 确定历史记录长度不超过风格总数-1（至少要留一个可选）
        history_size = min(MAX_STYLE_HISTORY, total_styles - 1) if total_styles > 1 else 0
        
        # 获取所有可用的风格索引
        available_styles = list(range(total_styles))
        
        # 如果有历史记录且风格数量大于1，则排除最近使用的风格
        if RECENT_USED_STYLES and total_styles > 1:
            # 从可用风格中移除最近使用的风格
            for style_idx in RECENT_USED_STYLES:
                if style_idx in available_styles:
                    available_styles.remove(style_idx)
        
        # 如果所有风格都被使用过（极端情况），则使用除最近一次外的任意风格
        if not available_styles and total_styles > 1:
            available_styles = list(range(total_styles))
            if RECENT_USED_STYLES:
                most_recent_style = RECENT_USED_STYLES[0]
                available_styles.remove(most_recent_style)
        
        # 从剩余的风格中随机选择一个
        style_index = random.choice(available_styles)
        
        if verbose:
            print_status(f"自动选择文章风格 {style_index + 1}（避免最近使用的风格）", "风格", Fore.CYAN)
        logger.info(f"自动选择文章风格 {style_index + 1}（避免最近使用的风格）")
    
    # 更新最近使用的风格历史
    RECENT_USED_STYLES.insert(0, style_index)  # 在列表开头插入新使用的风格
    # 保持历史记录不超过指定长度
    if len(RECENT_USED_STYLES) > MAX_STYLE_HISTORY:
        RECENT_USED_STYLES = RECENT_USED_STYLES[:MAX_STYLE_HISTORY]
    
    style_instructions = ARTICLE_STYLES[style_index]
    
    if verbose and RECENT_USED_STYLES:
        recent_styles_str = ", ".join([str(idx + 1) for idx in RECENT_USED_STYLES])
        print_status(f"最近使用的风格: {recent_styles_str}", "历史", Fore.CYAN)
    
    if RECENT_USED_STYLES:
        recent_styles_str = ", ".join([str(idx + 1) for idx in RECENT_USED_STYLES])
        logger.info(f"最近使用的风格历史: {recent_styles_str}")
    
    # 准备提示内容
    prompt = ARTICLE_PROMPT_TEMPLATE_BASE.format(
        title=news.get("title", ""),
        summary=news.get("summary", ""),
        link=news.get("link", ""),
        published_date=news.get("published_date", ""),
        style_instructions=style_instructions
    )
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            if verbose:
                print_status(f"正在使用模型 {model} 生成文章 (尝试 {attempt + 1}/{max_retries})", "生成", Fore.YELLOW)
                print_status(f"文章标题: {news.get('title')}", "标题", Fore.CYAN)
            
            logger.info(f"正在使用模型 {model} 生成文章: {news.get('title')} (尝试 {attempt + 1}/{max_retries})")
            
            # 显示生成进度
            if verbose:
                print_status("正在向OpenAI发送请求...", "请求", Fore.BLUE)
            
            # 调用OpenAI API
            start_time = time.time()
            response = client.chat.completions.create(
                model=model,  # 使用指定的模型
                messages=[
                    {"role": "system", "content": "你是一位专业的AI领域科技记者，擅长撰写社交媒体平台的爆款文章。你的文章充满情绪化表达、悬念设置和互动元素，能引发大量阅读、点赞和分享。你善于将复杂的AI技术用通俗易懂的方式解释。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 控制创造性
                max_tokens=2000,  # 最大输出长度
                top_p=0.95,
                frequency_penalty=0.5,  # 减少重复
                presence_penalty=0.5,  # 鼓励多样性
            )
            elapsed_time = time.time() - start_time
            
            # 提取生成的文章内容
            article_content = response.choices[0].message.content.strip()
            
            if article_content:
                if verbose:
                    print_status(f"文章生成成功: {len(article_content)} 字符，耗时: {elapsed_time:.2f}秒", "成功", Fore.GREEN)
                    # 显示文章预览
                    preview_length = min(200, len(article_content))
                    print_status(f"文章预览: {article_content[:preview_length]}...", "预览", Fore.CYAN)
                
                logger.info(f"文章生成成功: {len(article_content)} 字符，耗时: {elapsed_time:.2f}秒")
                return article_content
            else:
                if verbose:
                    print_status("生成的文章内容为空", "警告", Fore.YELLOW)
                logger.warning("生成的文章内容为空")
        
        except Exception as e:
            if verbose:
                print_status(f"生成文章时出错: {str(e)}", "错误", Fore.RED)
            logger.error(f"生成文章时出错: {str(e)}")
            
            # 如果不是最后一次尝试，则等待后重试
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                if verbose:
                    print_status(f"等待 {wait_time} 秒后重试...", "重试", Fore.YELLOW)
                    
                    # 显示等待进度条
                    with tqdm(total=wait_time, desc="等待重试", ncols=100, 
                              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}s") as pbar:
                        for _ in range(wait_time):
                            time.sleep(1)
                            pbar.update(1)
                else:
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
    
    if verbose:
        print_status(f"在 {max_retries} 次尝试后仍未能生成文章", "失败", Fore.RED)
    logger.error(f"在 {max_retries} 次尝试后仍未能生成文章")
    return None


def optimize_title(title: str, model: str = None, verbose: bool = False) -> str:
    """
    优化文章标题，使其更吸引人
    
    Args:
        title: 原始标题
        model: 要使用的模型名称，如果为None则使用默认模型
        verbose: 是否显示详细进度
        
    Returns:
        优化后的标题
    """
    if not OPENAI_API_KEY:
        if verbose:
            print_status("未设置API密钥，无法优化标题", "警告", Fore.YELLOW)
        logger.warning("未设置API密钥，无法优化标题")
        return title
    
    # 如果未指定模型，使用默认模型
    if model is None:
        model = DEFAULT_MODEL
    
    try:
        if verbose:
            print_status(f"正在使用模型 {model} 优化标题", "优化", Fore.BLUE)
            print_status(f"原标题: {title}", "原标题", Fore.CYAN)
        
        logger.info(f"正在使用模型 {model} 优化标题: {title}")
        
        # 显示优化进度
        if verbose:
            print_status("正在向OpenAI发送请求...", "请求", Fore.BLUE)
        
        # 调用OpenAI API
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位今日头条平台的爆款标题专家，擅长创作能引发大量点击和分享的标题。"},
                {"role": "user", "content": f"""请将以下AI新闻标题改写成今日头条平台的爆款标题，遵循以下规则：

1. 使用以下任一开头：
   - 震惊！
   - 重磅！
   - 突发！
   - 独家！
   - 紧急扩散！
   - 刚刚！

2. 或使用以下标题公式：
   - 数字清单：如"3个信号暗示AI已超越人类智能"
   - 悬念设问：如"AI真的能取代人类工作吗？答案让人意外"
   - 对比反差：如"曾被看衰的AI技术，如今竟能做到这一步"
   - 情感刺激：如"看完这个AI演示，所有人都惊呆了"

3. 标题要素：
   - 使用夸张但不失真的表达
   - 加入情绪化词汇
   - 制造信息差或悬念
   - 暗示稀缺或独家信息
   - 强调时效性和紧迫感

4. 长度控制在15-25字之间，确保吸引眼球但不过于冗长

原标题: {title}

请直接给出优化后的爆款标题，不要包含任何解释。"""}
            ],
            temperature=0.8,
            max_tokens=50,
            top_p=0.95,
        )
        elapsed_time = time.time() - start_time
        
        # 提取优化后的标题
        optimized_title = response.choices[0].message.content.strip()
        
        # 移除可能的引号和前缀
        optimized_title = optimized_title.replace('"', '').replace('"', '')
        optimized_title = optimized_title.replace('"', '').replace("'", "")
        optimized_title = optimized_title.replace("优化标题：", "").replace("优化后的标题：", "")
        
        if verbose:
            print_status(f"标题优化成功，耗时: {elapsed_time:.2f}秒", "成功", Fore.GREEN)
            print_status(f"优化后标题: {optimized_title}", "新标题", Fore.GREEN)
        
        logger.info(f"标题优化成功: {optimized_title}，耗时: {elapsed_time:.2f}秒")
        return optimized_title
    
    except Exception as e:
        if verbose:
            print_status(f"优化标题时出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"优化标题时出错: {str(e)}")
        return title


def get_available_models():
    """
    获取可用的模型列表
    
    Returns:
        可用模型列表
    """
    try:
        # 尝试从配置中获取可用模型列表
        return MODEL_CONFIG.get("available_models", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    except (NameError, AttributeError):
        # 如果配置不存在，返回默认列表
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="文章生成模块测试")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"要使用的OpenAI模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示详细的进度信息")
    parser.add_argument("--style", type=int, 
                        help=f"指定使用的文章风格 (1-{len(ARTICLE_STYLES)}), 不指定则自动选择")
    parser.add_argument("--history-size", type=int, default=MAX_STYLE_HISTORY,
                        help=f"记录的历史风格数量 (默认: {MAX_STYLE_HISTORY})")
    args = parser.parse_args()
    
    # 设置历史记录大小
    if args.history_size is not None and args.history_size >= 0:
        MAX_STYLE_HISTORY = args.history_size
        if args.verbose:
            print_status(f"设置历史风格记录数量为: {MAX_STYLE_HISTORY}", "配置", Fore.BLUE)
    
    # 测试数据
    test_news = {
        "title": "OpenAI发布GPT-4o，多模态能力大幅提升",
        "summary": "OpenAI今日发布了GPT-4o，这是一个具有强大多模态能力的大型语言模型，支持实时语音交互和视觉理解。",
        "link": "https://example.com/news/1",
        "published_date": "2023-05-20"
    }
    
    # 打印可用模型
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}文章生成模块测试{Style.RESET_ALL}")
    print(f"可用模型: {', '.join(get_available_models())}")
    print(f"默认模型: {Fore.GREEN}{DEFAULT_MODEL}{Style.RESET_ALL}")
    print(f"当前使用模型: {Fore.GREEN}{args.model}{Style.RESET_ALL}")
    print(f"显示详细进度: {Fore.GREEN}{args.verbose}{Style.RESET_ALL}")
    print(f"历史风格记录数量: {Fore.GREEN}{MAX_STYLE_HISTORY}{Style.RESET_ALL}")
    
    # 打印可用的风格
    print("\n可用的文章风格:")
    for i, style in enumerate(ARTICLE_STYLES):
        style_name = f"风格 {i+1}"
        if i == 0:
            style_name += " (今日头条爆款风格)"
        elif i == 1:
            style_name += " (知乎专业分析风格)"
        elif i == 2:
            style_name += " (微信公众号科普风格)"
        elif i == 3:
            style_name += " (商业分析报告风格)"
        print(f"{Fore.CYAN}{style_name}{Style.RESET_ALL}")
    
    if args.style:
        print(f"指定使用风格: {Fore.GREEN}{args.style}{Style.RESET_ALL}")
    
    print("=" * 60 + "\n")
    
    # 测试优化标题
    print_status("开始测试标题优化", "测试", Fore.BLUE)
    optimized_title = optimize_title(test_news["title"], model=args.model, verbose=args.verbose)
    print_status(f"优化后的标题: {optimized_title}", "结果", Fore.GREEN)
    
    # 测试生成文章
    print_status("开始测试文章生成", "测试", Fore.BLUE)
    article = generate_article(test_news, model=args.model, verbose=args.verbose, specific_style=args.style)
    
    if article:
        print_status("文章生成成功", "成功", Fore.GREEN)
        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}生成的文章内容:{Style.RESET_ALL}\n")
        print(article)
        print("\n" + "=" * 60)
    else:
        print_status("文章生成失败", "失败", Fore.RED) 