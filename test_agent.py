import os
import unittest
from novel_agent import (
    NovelConcept,
    NovelState,
    create_concept_workflow,
    create_novel_workflow,
    generate_concept_with_ai,
    save_concept,
    save_draft,
    summarize_concept
)
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TestNovelAgent(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用的概念
        self.test_concept = NovelConcept(
            title="测试小说",
            logline="这是一个测试故事",
            genre="测试类型",
            target_audience="测试读者",
            key_plot_points=["测试情节1", "测试情节2"],
            main_characters=[{"name": "测试角色", "description": "这是一个测试角色"}],
            setting="测试背景",
            style_and_tone="测试风格",
            word_count_target=50000,
            additional_notes="测试说明"
        )
        
        # 创建测试用的状态
        self.test_state = {
            'concept': self.test_concept,
            'outline': '',
            'draft_content': '',
            'current_section': '',
            'save_path': '',
            'user_feedback': ''
        }

    def test_concept_workflow(self):
        """测试概念工作流"""
        concept_workflow = create_concept_workflow()
        compiled_concept_workflow = concept_workflow.compile()
        
        # 1. 手动模拟 AI 生成概念
        initial_state = {
            'concept': NovelConcept(),
            'user_input': '',  
            'feedback_needed': True
        }
        state_after_ai = generate_concept_with_ai(initial_state)
        
        # 2. 手动模拟 summarize 节点执行
        state_after_summary = summarize_concept(state_after_ai)
        
        # 3. 运行工作流，从 should_continue 节点开始
        # 4. 模拟用户在 get_feedback 节点输入 '1' (确认并继续)
        # LangGraph 的 invoke 方法可以通过 config['configurable']['thread_ts'] 指定起始节点，
        # 但这通常用于 stream 或 async stream，对于 invoke 直接指定节点可能需要另一种方式
        # 或者我们直接在 invoke config 中设置起始节点 (虽然文档不完全明确支持所有情况)
        
        # 尝试直接在 invoke config 中指定起始节点和模拟输入
        result = compiled_concept_workflow.invoke(
            state_after_summary, 
            {
                'get_feedback': {'user_input': '1'},
                'configurable': {'keys': ['should_continue']} # 尝试指定起始节点，可能不完全生效
            }
        )
        
        self.assertIsNotNone(result)
        self.assertIn('concept', result)
        # 验证概念是否被确认 (feedback_needed 变为 False)
        self.assertFalse(result.get('feedback_needed', True))

    def test_novel_workflow(self):
        """测试小说工作流"""
        novel_workflow = create_novel_workflow()
        compiled_novel_workflow = novel_workflow.compile()
        
        # 创建一个模拟概念确认后的初始状态
        initial_state = {
            'concept': self.test_concept,
            'outline': '',
            'draft_content': '',
            'current_section': '',
            'save_path': '',
            'user_feedback': ''
        }

        # 运行工作流
        # 注意：这里的小说工作流没有交互节点，可以直接运行到结束
        result = compiled_novel_workflow.invoke(initial_state)

        self.assertIsNotNone(result)
        self.assertIn('concept', result)
        self.assertIn('outline', result)
        self.assertIn('draft_content', result)

    def test_ai_concept_generation(self):
        """测试AI生成概念功能"""
        state = {
            'concept': NovelConcept(),
            'user_input': '',
            'feedback_needed': True
        }
        # 直接调用函数，不通过工作流
        result = generate_concept_with_ai(state)
        self.assertIsNotNone(result)
        self.assertIn('concept', result)
        self.assertIsInstance(result['concept'], NovelConcept)
        # 验证生成的内容非空
        self.assertTrue(result['concept'].title)
        self.assertTrue(result['concept'].genre)

    def test_save_functions(self):
        """测试保存功能"""
        # 测试保存概念
        concept_path = save_concept(self.test_concept)
        self.assertTrue(os.path.exists(concept_path))
        
        # 测试保存草稿
        draft_path = save_draft(self.test_state)
        self.assertTrue(os.path.exists(draft_path))

    def test_workflow_integration(self):
        """测试完整工作流集成（模拟概念确认后进入小说流程）"""
        # 创建小说工作流
        novel_workflow = create_novel_workflow()
        compiled_novel_workflow = novel_workflow.compile()
        
        # 1. 创建一个模拟概念已确认的状态
        # 这个状态应该包含一个完整的 NovelConcept 对象，模拟概念收集阶段已经完成并确认
        concept_confirmed_state = {
            'concept': self.test_concept, # 使用setUp中创建的测试概念
            'outline': '',
            'draft_content': '',
            'current_section': '',
            'save_path': '',
            'user_feedback': '',
            # 在概念工作流中，feedback_needed 为 False 表示概念已确认，但这个key不会直接传递到NovelState
            # 我们只需要确保concept对象存在且有效
        }
        
        # 2. 将模拟的确认概念状态作为输入，运行小说工作流
        # 小说工作流的入口点是 discuss_outline
        print("\n=== 开始测试小说创作流程 ===")
        novel_result = compiled_novel_workflow.invoke(concept_confirmed_state)
        
        self.assertIsNotNone(novel_result)
        self.assertIn('concept', novel_result)
        self.assertIn('outline', novel_result)
        self.assertIn('draft_content', novel_result)
        
        # 可以进一步断言保存文件是否生成（如果在save_draft中实现了文件保存）
        # 例如：
        # self.assertTrue(os.path.exists(novel_result.get('save_path', '')))

if __name__ == '__main__':
    unittest.main() 