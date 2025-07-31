"""
统一Pipeline构建示例
演示如何使用新的统一构建方法创建RAGPipeline
"""

from core.pipeline.rag_pipeline import RAGPipelineBuilder, RAGConfig


def example_unified_pipeline():
    """演示统一Pipeline构建"""
    print("=== 统一Pipeline构建示例 ===")
    
    # 使用默认配置创建Pipeline
    pipeline1 = RAGPipelineBuilder.create_pipeline()
    print(f"默认Pipeline配置: {pipeline1.get_pipeline_info()}") 
    
    # 使用自定义配置创建Pipeline
    config = RAGConfig(
        chunk_size=500,
        chunk_overlap=50,
        parse_by_chapter=True
    )
    pipeline2 = RAGPipelineBuilder.create_pipeline(config)
    print(f"自定义Pipeline配置: {pipeline2.get_pipeline_info()}")
    
    # 使用已废弃的方法（会显示警告）
    print("\n使用已废弃的方法:")
    pipeline3 = RAGPipelineBuilder.create_academic_pipeline()
    print(f"学术文档Pipeline配置: {pipeline3.get_pipeline_info()}")


def main():
    example_unified_pipeline()


if __name__ == "__main__":
    main()