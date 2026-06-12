# Project Analysis — Heurísticas de Detecção de Stack

## 1. Detecção de Linguagem

| Sinal | Linguagem |
|-------|-----------|
| Arquivos `.py` presentes | Python |
| Arquivos `.js` ou `.ts` presentes | Node.js / JavaScript |
| `package.json` na raiz | Node.js |
| `requirements.txt` ou `pyproject.toml` | Python |
| `go.mod` | Go |
| `pom.xml` | Java/Maven |

**Procedimento:** listar todos os arquivos na raiz e subpastas com extensão; a extensão mais frequente define a linguagem principal.

---

## 2. Detecção de Framework

### Python
| Sinal | Framework |
|-------|-----------|
| `from flask import Flask` | Flask |
| `from django.` | Django |
| `from fastapi import FastAPI` | FastAPI |
| `from starlette` | Starlette |

### Node.js
| Sinal | Framework |
|-------|-----------|
| `require('express')` ou `import express` | Express |
| `require('fastify')` | Fastify |
| `require('koa')` | Koa |
| `require('@nestjs/core')` | NestJS |

**Procedimento:** grep por imports/requires nos arquivos de entrada (app.py, app.js, index.js, main.py).

---

## 3. Detecção de Banco de Dados

| Sinal | Banco |
|-------|-------|
| `import sqlite3` (Python) ou `require('sqlite3')` (Node) | SQLite |
| `sqlite3.Database(':memory:')` | SQLite in-memory |
| `import psycopg2` / `psycopg` | PostgreSQL |
| `from sqlalchemy` / `Flask-SQLAlchemy` | SQLAlchemy ORM |
| `require('mongoose')` | MongoDB |
| `require('sequelize')` | Sequelize ORM (MySQL/Postgres/SQLite) |
| `require('pg')` | PostgreSQL |

**Tabelas:** para SQLite, procurar por `CREATE TABLE` nos arquivos `.py`/`.js`; para ORM, listar classes que herdam de `db.Model` ou `Model`.

---

## 4. Mapeamento de Arquitetura

### Indicadores de Monolito (sem separação de camadas)
- Menos de 5 arquivos de código-fonte na raiz
- Arquivo único > 200 linhas com rotas, lógica de negócio e acesso a dados
- Sem pastas `models/`, `controllers/`, `routes/`, `services/`

### Indicadores de Arquitetura em Camadas
- Pastas `models/`, `controllers/`, `routes/`, `services/` presentes
- Arquivos de entrada delegam para módulos especializados
- Importações cruzam camadas de forma unidirecional (route → controller → model)

### Indicadores de MVC Correto
- Model: apenas acesso a dados, sem lógica de negócio
- Controller: orquestra model + regras, sem HTTP direto
- View/Route: apenas validação de input + chamada de controller + serialização de response
- Configuração centralizada em `config/` usando variáveis de ambiente

---

## 5. Contagem de Arquivos e LOC

Incluir na análise:
- Todos os `.py` exceto `__init__.py` vazios e arquivos de migração
- Todos os `.js`/`.ts` exceto `node_modules/` e arquivos de build
- Contar linhas com `wc -l` ou equivalente

---

## 6. Detecção de Domínio da Aplicação

Analisar nomes de tabelas, rotas e variáveis para identificar o domínio:

| Palavras-chave encontradas | Domínio provável |
|---------------------------|-----------------|
| `produto`, `pedido`, `estoque`, `carrinho` | E-commerce / Loja |
| `task`, `tarefa`, `categoria`, `assignee` | Task Manager |
| `curso`, `matricula`, `enrollment`, `aluno` | LMS / Educação |
| `usuario`, `user`, `auth`, `login` | Sistema de autenticação |
| `relatorio`, `report`, `revenue` | Analytics / BI |

---

## 7. Formato de Saída da Fase 1

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework + versão do requirements.txt/package.json>
Dependencies:  <lista das dependências principais>
Domain:        <domínio inferido do negócio>
Architecture:  <descrição em 1 frase da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <lista das tabelas detectadas>
================================
```
