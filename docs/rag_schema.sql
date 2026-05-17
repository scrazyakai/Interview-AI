-- ============================================================
-- RAG 模块数据库初始化 DDL
-- 执行顺序：按文件从上到下依次执行
-- ============================================================

-- 1. 启用 pgvector 扩展（需要超级用户权限，执行一次即可）
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 创建 rag schema
CREATE SCHEMA IF NOT EXISTS rag;

-- ============================================================
-- 3. 文档原始内容表
--    存储管理员上传的原始文档，保留完整内容便于审计和重建索引
-- ============================================================
CREATE TABLE IF NOT EXISTS rag.documents (
    id              BIGSERIAL PRIMARY KEY,
    doc_uuid        UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL,              -- 保留原始文本
    file_name       VARCHAR(255) NOT NULL,
    file_type       VARCHAR(20) NOT NULL,         -- pdf / txt / md
    category        VARCHAR(50) NOT NULL DEFAULT 'general',
                                                  -- frontend / backend / database
                                                  -- algorithm / behavioral / general
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
                                                  -- pending / indexed / failed
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    created_by      UUID NOT NULL,               -- 上传的管理员 user_id
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. 文档分块 + 向量嵌入表
--    doc_id 通过 CASCADE 与 documents 绑定，删文档时自动清理
-- ============================================================
CREATE TABLE IF NOT EXISTS rag.document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    doc_id      BIGINT NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text  TEXT NOT NULL,
    embedding   VECTOR(1024),                    -- text-embedding-v3 维度 1024
    metadata    JSONB,                           -- doc_uuid / category / chunk_index
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. 索引
-- ============================================================

-- 文档按创建时间倒序分页
CREATE INDEX IF NOT EXISTS idx_rag_documents_created_at
    ON rag.documents (created_at DESC);

-- chunk 按 doc_id 快速关联
CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc_id
    ON rag.document_chunks (doc_id);

-- pgvector HNSW 近似最近邻索引（余弦相似度）
-- 建议在数据量 > 1000 条后再创建，少量数据顺序扫描更快
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding_hnsw
    ON rag.document_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- 6. 同步 interview.users 表：role_type 补默认值
--    若已有历史用户 role_type 为 NULL，统一设为普通用户(1)
-- ============================================================
ALTER TABLE interview.users
    ALTER COLUMN role_type SET DEFAULT 1;

UPDATE interview.users
   SET role_type = 1
 WHERE role_type IS NULL;

ALTER TABLE interview.users
    ALTER COLUMN role_type SET NOT NULL;
