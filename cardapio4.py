
# -- coding: utf-8 --
import sqlite3
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Conexão com o banco de dados
conn = sqlite3.connect("cardapio.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    prato TEXT NOT NULL
)
""")
conn.commit()

# Corrigir prato com erro de digitação no banco
cursor.execute("UPDATE pedidos SET prato = 'panelada' WHERE prato = 'paindada'")
conn.commit()

# Lista de pratos
pratos = ["cozidão", "peixe frito", "assado de panela", "frango frito",
          "porco frito", "chambari", "galinha caipira", "Panelada"]

st.title("Sistema de Pedidos - Cardápio")

st.subheader("Escolha seu prato")
nome = st.text_input("Digite seu nome")
escolha = st.selectbox("Escolha um prato:", pratos)

if st.button("Registrar Pedido"):
    if nome and escolha:
        cursor.execute("INSERT INTO pedidos (nome, prato) VALUES (?, ?)", (nome, escolha))
        conn.commit()
        st.success(f"{nome} escolheu {escolha} para o almoço")
    else:
        st.error("Por favor, preencha seu nome e escolha um prato.")

# Administração
st.subheader("Administração")
senha = st.text_input("Digite a senha para excluir todos os pedidos", type="password")
if st.button("Apagar todos os registros"):
    if senha == "1234":
        cursor.execute("DELETE FROM pedidos")
        conn.commit()
        st.success("Todos os registros foram apagados.")
    else:
        st.error("Senha incorreta. A exclusão foi cancelada.")

# Consultar e exibir pedidos
cursor.execute("SELECT nome, prato FROM pedidos")
todos_pedidos = cursor.fetchall()

df_pedidos = pd.DataFrame(todos_pedidos, columns=["Nome", "Prato"])
df_resumo = df_pedidos.groupby("Prato").size().reset_index(name="Quantidade")

st.markdown("### Tabela de Pedidos")
st.dataframe(df_pedidos)

st.markdown("### Resumo por Prato")
st.dataframe(df_resumo)

total = df_pedidos.shape[0]
st.write(f"*Total de pratos escolhidos:* {total}")

# Função para gerar PDF com duas tabelas
def gerar_pdf_completo(df_pedidos, df_resumo, nome_arquivo="resumo_pedidos.pdf"):
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    estilos = getSampleStyleSheet()
    elementos = []

    # Título
    elementos.append(Paragraph("Resumo de Pedidos", estilos['Title']))
    elementos.append(Spacer(1, 12))

    # Tabela 1: Pedidos detalhados
    elementos.append(Paragraph("Pedidos Individuais", estilos['Heading2']))
    data1 = [["Nome", "Prato"]] + df_pedidos.values.tolist()
    tabela1 = Table(data1, colWidths=[200, 200])
    tabela1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightyellow])
    ]))
    elementos.append(tabela1)
    elementos.append(Spacer(1, 20))

    # Tabela 2: Resumo por prato
    elementos.append(Paragraph("Resumo por Prato", estilos['Heading2']))
    data2 = [["Prato", "Quantidade"]] + df_resumo.values.tolist()
    tabela2 = Table(data2, colWidths=[200, 100])
    tabela2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightcyan])
    ]))
    elementos.append(tabela2)

    doc.build(elementos)

# Gerar PDF e permitir download
if not df_pedidos.empty:
    gerar_pdf_completo(df_pedidos, df_resumo)
    with open("resumo_pedidos.pdf", "rb") as pdf_file:
        st.download_button("Baixar resumo em PDF", pdf_file, file_name="resumo_pedidos.pdf", mime="application/pdf")