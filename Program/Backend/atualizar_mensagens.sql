-- Primeiro, adicionar a coluna sender
ALTER TABLE message ADD COLUMN sender VARCHAR(10);

-- Atualizar mensagens existentes com um valor padrão
UPDATE message 
SET sender = CASE 
    WHEN id % 2 = 0 THEN 'user'
    ELSE 'assistant'
END;

-- Adicionar a constraint NOT NULL
ALTER TABLE message ALTER COLUMN sender SET NOT NULL;

-- Adicionar a constraint CHECK para garantir valores válidos
ALTER TABLE message ADD CONSTRAINT check_sender CHECK (sender IN ('user', 'assistant')); 