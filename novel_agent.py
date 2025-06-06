import os
from typing import Dict, List, Optional, TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel
from dashscope import Generation
from datetime import datetime
import openai

# 加载环境变量
load_dotenv()

# 定义状态类型
class NovelState(TypedDict):
    project_name: str
    outline: str
    content: str
    current_chapter: int
    total_chapters: int
    working_dir: str
    mode: str  # 'new' 或 'edit'

class NovelConcept(BaseModel):
    """小说概念模型"""
    title: str = ""
    logline: str = "" # 故事一句话概括
    genre: str = "" # 类型 (例如：科幻、奇幻、推理)
    target_audience: str = "" # 目标读者
    key_plot_points: List[str] = [] # 关键情节
    main_characters: List[Dict] = [] # 主要角色 (包含姓名、简介等)
    setting: str = "" # 背景设定
    style_and_tone: str = "" # 文风和语调
    word_count_target: int = 0 # 目标字数
    additional_notes: str = "" # 补充说明

class ConceptState(TypedDict):
    """概念收集状态"""
    concept: NovelConcept
    user_input: str # 用户输入
    feedback_needed: bool # 是否需要用户反馈

# 定义节点函数
def discuss_outline(state: NovelState) -> NovelState:
    """与用户讨论并确定小说大纲"""
    # TODO: 实现与用户的交互逻辑
    return state

def create_initial_draft(state: NovelState) -> NovelState:
    """根据大纲创建初稿"""
    # TODO: 调用Qwen模型生成初稿
    return state

def save_draft(state: NovelState) -> NovelState:
    """保存稿件到本地"""
    project_dir = os.path.join(state['working_dir'], state['project_name'])
    os.makedirs(project_dir, exist_ok=True)
    
    # 保存大纲
    with open(os.path.join(project_dir, 'outline.txt'), 'w', encoding='utf-8') as f:
        f.write(state['outline'])
    
    # 保存内容
    with open(os.path.join(project_dir, 'content.txt'), 'w', encoding='utf-8') as f:
        f.write(state['content'])
    
    return state

def modify_outline(state: NovelState) -> NovelState:
    """修改小说大纲"""
    # TODO: 实现大纲修改逻辑
    return state

def modify_content(state: NovelState) -> NovelState:
    """修改小说内容"""
    # TODO: 实现内容修改逻辑
    return state

def should_continue(state: NovelState) -> str:
    """决定下一步操作"""
    # TODO: 实现决策逻辑
    return "continue"

def generate_concept_with_ai(state: ConceptState) -> ConceptState:
    """使用 AI 生成小说概念"""
    print("\n=== AI 正在生成小说概念 ===")

    # 构建提示词
    prompt = """请帮我生成一个完整的小说概念，包括以下要素：
1. 标题
2. 类型（如：奇幻、科幻、言情等）
3. 主要主题
4. 目标读者群体
5. 故事背景设定
6. 写作风格
7. 预计字数
8. 主要人物（至少3个，包含姓名、角色和特点）
9. 关键情节点（至少5个）
10. 其他补充说明

请严格按照以下格式输出，确保每个字段都有对应的值，即使没有也用占位符表示（如：补充说明：无）：
标题：[标题]
类型：[类型]
主题：[主题]
目标读者：[目标读者]
背景设定：[背景设定]
写作风格：[写作风格]
预计字数：[字数，只包含数字]

主要人物：
[姓名] - [角色]：[特点]
[姓名] - [角色]：[特点]
[姓名] - [角色]：[特点]
（如果少于3个，列出所有人物）

关键情节点：
- [情节点1]
- [情节点2]
- [情节点3]
- [情节点4]
- [情节点5]
（如果少于5个，列出所有情节点）

补充说明：[补充说明]
"""

    try:
        # 使用 OpenAI 兼容模式调用 Qwen 模型
        client = openai.OpenAI(
            api_key=os.getenv("QWEN_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        response = client.chat.completions.create(
            model=os.getenv("QWEN_MODEL_NAME", "qwen3-235b-a22b"),
            messages=[
                {"role": "system", "content": "你是一个善于创作小说的AI助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=float(os.getenv("QWEN_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("QWEN_MAX_TOKENS", "2048")),
            extra_body={"enable_thinking": False},
        )

        if response.choices and response.choices[0].message.content:
            # 解析 AI 生成的文本
            generated_text = response.choices[0].message.content
            lines = generated_text.split('\n')

            concept = state['concept']
            current_section = ""
            temp_characters = [] # 临时存储人物列表
            temp_plot_points = [] # 临时存储情节点列表

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('标题：'):
                    concept.title = line[3:].strip()
                elif line.startswith('类型：'):
                    concept.genre = line[3:].strip()
                elif line.startswith('主题：'):
                    concept.logline = line[3:].strip()
                elif line.startswith('目标读者：'):
                    concept.target_audience = line[5:].strip()
                elif line.startswith('背景设定：'):
                    concept.setting = line[5:].strip()
                elif line.startswith('写作风格：'):
                    concept.style_and_tone = line[5:].strip()
                elif line.startswith('预计字数：'):
                    try:
                        concept.word_count_target = int(''.join(filter(str.isdigit, line[5:].strip())))
                    except ValueError:
                        concept.word_count_target = 50000  # 默认值
                elif line == '主要人物：':
                    current_section = 'characters'
                elif line == '关键情节点：':
                    current_section = 'plot'
                elif line.startswith('补充说明：'):
                    current_section = 'notes'
                    concept.additional_notes = line[5:].strip() # 直接获取补充说明的第一行
                elif current_section == 'characters' and ' - ' in line and '：' in line:
                     try:
                         parts = line.split('：', 1)
                         name_role = parts[0].strip()
                         traits = parts[1].strip() if len(parts) > 1 else ""
                         name, role = name_role.split(' - ', 1)
                         temp_characters.append({
                             "name": name.strip(),
                             "role": role.strip(),
                             "traits": traits
                         })
                     except ValueError:
                         continue # 忽略格式不符的行
                elif current_section == 'plot' and line.startswith('- '):
                    temp_plot_points.append(line[2:].strip())
                elif current_section == 'notes':
                     concept.additional_notes += '\n' + line # 追加补充说明的其他行

            # 更新列表字段
            concept.main_characters = temp_characters
            concept.key_plot_points = temp_plot_points

            print("AI 已生成小说概念，请查看并确认。")
        else:
            print("AI 生成失败，请手动输入小说概念。")
            # 恢复到手动输入流程
            state['user_input'] = "AI生成失败"
            return collect_initial_concept(state)

    except Exception as e:
        print(f"AI 生成出错：{str(e)}")
        print("请手动输入小说概念。")
        # 恢复到手动输入流程
        state['user_input'] = f"AI生成出错：{str(e)}"
        return collect_initial_concept(state)

    return state

def collect_initial_concept(state: ConceptState) -> ConceptState:
    """收集用户初始概念"""
    print("\n=== 小说概念收集 ===")
    print("请选择概念收集方式：")
    print("1. 手动输入")
    print("2. AI 自动生成")
    
    choice = input("\n请选择（1-2）：")
    
    if choice == "2":
        return generate_concept_with_ai(state)
    
    print("\n请回答以下问题来帮助我们理解您的小说构想：")
    
    state['concept'].title = input("1. 小说的暂定标题是什么？")
    state['concept'].genre = input("2. 您期望的小说类型是什么？（如：奇幻、科幻、言情等）")
    state['concept'].logline = input("3. 故事的一句话概括是什么？")
    state['concept'].target_audience = input("4. 目标读者群体是？")
    state['concept'].setting = input("5. 故事发生的背景设定是？")
    state['concept'].style_and_tone = input("6. 期望的写作风格是？（如：轻松、严肃、悬疑等）")
    state['concept'].word_count_target = int(input("7. 预计字数目标是多少？"))
    
    print("\n8. 请描述主要人物（每行一个，格式：姓名,角色,特点）：")
    while True:
        char_input = input("输入人物信息（直接回车结束）：")
        if not char_input:
            break
        name, role, traits = char_input.split(',')
        state['concept'].main_characters.append({
            "name": name.strip(),
            "role": role.strip(),
            "traits": traits.strip()
        })
    
    print("\n9. 请描述关键情节点（每行一个）：")
    while True:
        plot_point = input("输入情节点（直接回车结束）：")
        if not plot_point:
            break
        state['concept'].key_plot_points.append(plot_point)
    
    state['user_input'] = input("\n10. 其他补充说明：")
    return state

def summarize_concept(state: ConceptState) -> ConceptState:
    """总结并展示当前概念"""
    concept = state['concept']
    print("\n=== 当前小说概念总结 ===")
    print(f"标题：{concept.title}")
    print(f"类型：{concept.genre}")
    print(f"主题：{concept.logline}")
    print(f"目标读者：{concept.target_audience}")
    print(f"背景设定：{concept.setting}")
    print(f"写作风格：{concept.style_and_tone}")
    print(f"目标字数：{concept.word_count_target}")
    
    print("\n主要人物：")
    for char in concept.main_characters:
        print(f"- {char['name']}（{char['role']}）：{char['traits']}")
    
    print("\n关键情节点：")
    for i, point in enumerate(concept.key_plot_points, 1):
        print(f"{i}. {point}")
    
    if concept.additional_notes:
        print(f"\n补充说明：{concept.additional_notes}")
    
    return state

def get_user_feedback(state: ConceptState) -> ConceptState:
    """获取用户反馈"""
    print("\n=== 概念确认 ===")
    print("请确认以上概念是否符合您的期望：")
    print("1. 确认并继续")
    print("2. 需要修改")
    print("3. 重新开始")
    
    choice = input("\n请选择（1-3）：")
    
    if choice == "1":
        state['feedback_needed'] = False
        state['user_input'] = "用户确认概念"
    elif choice == "2":
        state['feedback_needed'] = True
        state['user_input'] = input("请说明需要修改的部分：")
    else:
        state['feedback_needed'] = True
        state['user_input'] = "重新开始"
        state['iteration_count'] = 0
    
    return state

def modify_concept(state: ConceptState) -> ConceptState:
    """根据反馈修改概念"""
    if state['user_input'] == "重新开始":
        return collect_initial_concept(state)
    
    print("\n=== 修改概念 ===")
    print("请选择要修改的部分：")
    print("1. 标题")
    print("2. 类型")
    print("3. 主题")
    print("4. 目标读者")
    print("5. 背景设定")
    print("6. 写作风格")
    print("7. 目标字数")
    print("8. 主要人物")
    print("9. 关键情节点")
    print("10. 补充说明")
    
    choice = input("\n请选择要修改的项目（1-10）：")
    concept = state['concept']
    
    if choice == "1":
        concept.title = input("新的标题：")
    elif choice == "2":
        concept.genre = input("新的类型：")
    elif choice == "3":
        concept.logline = input("新的主题：")
    elif choice == "4":
        concept.target_audience = input("新的目标读者：")
    elif choice == "5":
        concept.setting = input("新的背景设定：")
    elif choice == "6":
        concept.style_and_tone = input("新的写作风格：")
    elif choice == "7":
        concept.word_count_target = int(input("新的目标字数："))
    elif choice == "8":
        print("当前人物列表：")
        for i, char in enumerate(concept.main_characters, 1):
            print(f"{i}. {char['name']}（{char['role']}）：{char['traits']}")
        print("\n1. 添加新人物")
        print("2. 修改现有人物")
        print("3. 删除人物")
        sub_choice = input("请选择操作（1-3）：")
        if sub_choice == "1":
            name = input("姓名：")
            role = input("角色：")
            traits = input("特点：")
            concept.main_characters.append({"name": name, "role": role, "traits": traits})
        elif sub_choice == "2":
            idx = int(input("要修改的人物编号：")) - 1
            if 0 <= idx < len(concept.main_characters):
                concept.main_characters[idx]["name"] = input("新的姓名：")
                concept.main_characters[idx]["role"] = input("新的角色：")
                concept.main_characters[idx]["traits"] = input("新的特点：")
        elif sub_choice == "3":
            idx = int(input("要删除的人物编号：")) - 1
            if 0 <= idx < len(concept.main_characters):
                concept.main_characters.pop(idx)
    elif choice == "9":
        print("当前情节点列表：")
        for i, point in enumerate(concept.key_plot_points, 1):
            print(f"{i}. {point}")
        print("\n1. 添加新情节点")
        print("2. 修改现有情节点")
        print("3. 删除情节点")
        sub_choice = input("请选择操作（1-3）：")
        if sub_choice == "1":
            concept.key_plot_points.append(input("新的情节点："))
        elif sub_choice == "2":
            idx = int(input("要修改的情节点编号：")) - 1
            if 0 <= idx < len(concept.key_plot_points):
                concept.key_plot_points[idx] = input("新的情节点：")
        elif sub_choice == "3":
            idx = int(input("要删除的情节点编号：")) - 1
            if 0 <= idx < len(concept.key_plot_points):
                concept.key_plot_points.pop(idx)
    elif choice == "10":
        concept.additional_notes = input("新的补充说明：")
    
    return state

def should_continue_concept(state: ConceptState) -> str:
    """判断是否需要继续概念收集"""
    if state.get('feedback_needed', False):
        return "need_feedback"
    return "confirmed"

# 创建工作流图
def create_novel_workflow() -> StateGraph:
    """创建小说创作工作流"""
    workflow = StateGraph(NovelState)
    
    # 添加节点
    workflow.add_node("discuss_outline", discuss_outline)
    workflow.add_node("create_draft", create_initial_draft)
    workflow.add_node("save", save_draft)
    workflow.add_node("modify_outline", modify_outline)
    workflow.add_node("modify_content", modify_content)
    workflow.add_node("should_continue", should_continue)
    
    # 设置边
    workflow.add_edge("discuss_outline", "create_draft")
    workflow.add_edge("create_draft", "save")
    workflow.add_edge("save", "should_continue")
    workflow.add_conditional_edges(
        "should_continue",
        should_continue,
        {
            "modify_outline": "modify_outline",
            "modify_content": "modify_content",
            "completed": END # 使用END表示终止
        }
    )
    workflow.add_edge("modify_outline", "create_draft")
    workflow.add_edge("modify_content", "save")
    
    # 设置入口
    workflow.set_entry_point("discuss_outline")
    
    return workflow

def create_concept_workflow() -> StateGraph:
    """创建概念收集工作流"""
    workflow = StateGraph(ConceptState)
    
    # 添加节点
    workflow.add_node("collect_concept", collect_initial_concept)
    workflow.add_node("summarize", summarize_concept)
    workflow.add_node("get_feedback", get_user_feedback)
    workflow.add_node("modify", modify_concept)
    workflow.add_node("should_continue", should_continue_concept)
    
    # 设置边
    workflow.add_edge("collect_concept", "summarize")
    workflow.add_edge("summarize", "should_continue")
    workflow.add_conditional_edges(
        "should_continue",
        should_continue_concept,
        {
            "need_feedback": "get_feedback",
            "confirmed": END # 使用END表示终止
        }
    )
    workflow.add_edge("get_feedback", "modify")
    workflow.add_edge("modify", "summarize")
    
    # 设置入口
    workflow.set_entry_point("collect_concept")
    
    return workflow

def save_concept(concept: NovelConcept) -> str:
    """保存小说概念到文件"""
    # 确保工作目录存在
    working_dir = os.getenv("NOVEL_WORKING_DIR", "./novels")
    os.makedirs(working_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"{concept.title}_concept.txt"
    filepath = os.path.join(working_dir, filename)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"标题：{concept.title}\n")
        f.write(f"类型：{concept.genre}\n")
        f.write(f"目标读者：{concept.target_audience}\n")
        f.write(f"背景设定：{concept.setting}\n")
        f.write(f"写作风格：{concept.style_and_tone}\n")
        f.write(f"目标字数：{concept.word_count_target}\n\n")
        
        f.write("主要人物：\n")
        for character in concept.main_characters:
            f.write(f"- {character['name']}：{character['description']}\n")
        
        f.write("\n关键情节点：\n")
        for point in concept.key_plot_points:
            f.write(f"- {point}\n")
        
        if concept.additional_notes:
            f.write(f"\n补充说明：{concept.additional_notes}\n")
    
    print(f"小说概念已保存到：{filepath}")
    return filepath

def save_draft(state: NovelState) -> str:
    """保存小说草稿到文件"""
    # 确保工作目录存在
    working_dir = os.getenv("NOVEL_WORKING_DIR", "./novels")
    os.makedirs(working_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"{state['concept'].title}_draft.txt"
    filepath = os.path.join(working_dir, filename)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"=== {state['concept'].title} ===\n\n")
        f.write(f"大纲：\n{state['outline']}\n\n")
        f.write(f"内容：\n{state['draft_content']}\n")
        
    print(f"小说草稿已保存到：{filepath}")
    return filepath

# 导出所有需要的函数和类
__all__ = [
    "NovelConcept",
    "NovelState",
    "create_concept_workflow",
    "create_novel_workflow",
    "generate_concept_with_ai",
    "save_concept",
    "save_draft"
]

if __name__ == "__main__":
    # 创建概念工作流
    concept_workflow = create_concept_workflow()
    compiled_concept_workflow = concept_workflow.compile()
    
    # 创建小说工作流
    novel_workflow = create_novel_workflow()
    compiled_novel_workflow = novel_workflow.compile()
    
    # 运行概念工作流
    concept_state = {
        'concept': NovelConcept(),
        'user_input': '',
        'feedback_needed': True
    }
    concept_result = compiled_concept_workflow.invoke(concept_state)
    
    # 如果概念被确认，运行小说工作流
    if not concept_result.get('feedback_needed', True):
        novel_state = {
            'concept': concept_result['concept'],
            'outline': '',
            'draft_content': '',
            'current_section': '',
            'save_path': '',
            'user_feedback': ''
        }
        novel_result = compiled_novel_workflow.invoke(novel_state)
        print("\n=== 小说创作完成 ===")
        print(f"大纲：\n{novel_result['outline']}")
        print(f"\n内容：\n{novel_result['draft_content']}") 