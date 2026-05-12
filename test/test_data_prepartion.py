"""
测试数据准备模块
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.data_preparation import DataPreparation


def main():
    # 初始化数据准备模块
    question_bank_path = "app/docs/question_bank.md"

    print("=" * 60)
    print("RAG 数据准备模块测试")
    print("=" * 60)

    # 创建数据准备实例
    data_prep = DataPreparation(question_bank_path)

    # 加载文档
    print(f"\n📂 正在加载题库: {question_bank_path}")
    documents = data_prep.load_documents()

    print(f"✅ 成功加载 {len(documents)} 个题目\n")

    # 显示统计信息
    print("📊 题库统计信息:")
    print("-" * 60)
    stats = data_prep.get_statistics()

    print(f"总题目数: {stats['total_questions']}")

    print("\n技术栈分布:")
    for skill, count in sorted(stats['skill_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {skill}: {count} 题")

    print("\n难度分布:")
    for difficulty, count in stats['difficulty_distribution'].items():
        print(f"  - {difficulty}: {count} 题")

    print("\n题目类型分布:")
    for qtype, count in sorted(stats['type_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {qtype}: {count} 题")

    # 显示前 3 个题目示例
    print("\n" + "=" * 60)
    print("📝 题目示例（前 3 题）:")
    print("=" * 60)

    for i, doc in enumerate(documents[:3], 1):
        print(f"\n【题目 {i}】")
        print(f"标题: {doc.metadata['question_title']}")
        print(f"技术栈: {', '.join(doc.metadata['skills'])}")
        print(f"难度: {doc.metadata['difficulty']}")
        print(f"类型: {doc.metadata['question_type']}")
        print(f"关键词: {', '.join(doc.metadata['keywords'][:5])}")
        print(f"内容预览: {doc.page_content[:150]}...")
        print("-" * 60)

    # 测试按技术栈筛选
    print("\n" + "=" * 60)
    print("🔍 按技术栈筛选测试:")
    print("=" * 60)

    java_docs = data_prep.get_documents_by_skill("Java")
    print(f"Java 相关题目: {len(java_docs)} 题")

    db_docs = data_prep.get_documents_by_skill("数据库")
    print(f"数据库相关题目: {len(db_docs)} 题")

    concurrent_docs = data_prep.get_documents_by_skill("并发")
    print(f"并发相关题目: {len(concurrent_docs)} 题")

    # 测试按难度筛选
    print("\n" + "=" * 60)
    print("🎯 按难度筛选测试:")
    print("=" * 60)

    easy_docs = data_prep.get_documents_by_difficulty("easy")
    print(f"简单题目: {len(easy_docs)} 题")

    medium_docs = data_prep.get_documents_by_difficulty("medium")
    print(f"中等题目: {len(medium_docs)} 题")

    hard_docs = data_prep.get_documents_by_difficulty("hard")
    print(f"困难题目: {len(hard_docs)} 题")

    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
