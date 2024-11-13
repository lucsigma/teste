
import sqlite3
import streamlit as st
import pandas as pd

# Conectar ao banco de dados SQLite (ou criar um novo)
conn = sqlite3.connect('presencas0100.db')
c = conn.cursor()

# Função para criar tabela se não existir
def criar_tabela(nome_tabela):
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {nome_tabela} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT,
            dia DATE,
            presenca TEXT
        )
    ''')
    conn.commit()

# Criar uma tabela de controle para o estado de bloqueio
def criar_tabela_controle():
    c.execute('''
        CREATE TABLE IF NOT EXISTS controle (
            id INTEGER PRIMARY KEY,
            estado_bloqueio INTEGER
        )
    ''')
    conn.commit()

# Função para definir o estado de bloqueio
def set_bloqueio(estado):
    c.execute('''REPLACE INTO controle (id, estado_bloqueio) VALUES (1, ?)''', (estado,))
    conn.commit()

# Função para obter o estado de bloqueio
def get_bloqueio():
    c.execute('''SELECT estado_bloqueio FROM controle WHERE id = 1''')
    resultado = c.fetchone()
    return resultado[0] if resultado else 0  # 0 significa desbloqueado, 1 significa bloqueado

# Função para registrar a presença
def registrar_presenca(funcionario, dia, presenca, tabela):
    c.execute(f'INSERT INTO {tabela} (funcionario, dia, presenca) VALUES (?, ?, ?)', (funcionario, dia, presenca))
    conn.commit()

# Função para listar presenças de uma tabela específica
def listar_presencas(tabela):
    c.execute(f'SELECT * FROM {tabela}')
    df = pd.DataFrame(c.fetchall(), columns=['ID', 'Funcionário', 'Dia', 'Presença'])

    df['Dia'] = pd.to_datetime(df['Dia'])
    df['Dia da Semana'] = df['Dia'].dt.dayofweek.map(dias_da_semana_pt)

    df['Data'] = df['Dia'].dt.strftime('%d/%m/%Y')
    df = df[['Funcionário', 'Data', 'Dia da Semana', 'Presença']]

    return df

# Função para excluir todas as presenças
def excluir_relatorio(senha, tabela):
    if senha == "  .defcon1 . ":
        c.execute(f'DELETE FROM {tabela}')
        conn.commit()
        return True
    return False

# Função para bloquear o aplicativo
def bloquear_aplicativo(senha):
    if senha == "9045":
        set_bloqueio(1)  # Definir como bloqueado no banco
        st.session_state.trancado = True
        return True
    return False

# Função para destrancar o aplicativo
def destrancar_aplicativo(senha):
    if senha == "9045":
        set_bloqueio(0)  # Definir como desbloqueado no banco
        st.session_state.trancado = False
        return True
    return False

# Dicionário para mapear os dias da semana em português
dias_da_semana_pt = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

# Criar tabelas para diferentes departamentos ou equipes
tabelas = [f'relatorio{i+1}' for i in range(10)]  # 10 tabelas
for tabela in tabelas:
    criar_tabela(tabela)

# Criar tabela de controle
criar_tabela_controle()

# Inicializar o estado de bloqueio da sessão com base no banco de dados
if 'trancado' not in st.session_state:
    st.session_state.trancado = get_bloqueio() == 1

# Interface Streamlit
st.title("Registro de Presenças")
st.markdown("### Preencha os dados abaixo para registrar a presença dos funcionários")

if not st.session_state.trancado:
    # Organizando campos de entrada em colunas
    with st.form("registro_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            funcionario = st.text_input("Nome do Funcionário")
        with col2:
            dia = st.date_input("Data")
        with col3:
            presenca = st.selectbox("Presença", ["manhã_e_tarde", "só_manhã", "só_tarde"])

        tabela_selecionada = st.selectbox("Selecione a tabela", tabelas)

        submit_button = st.form_submit_button("Registrar Presença")
        if submit_button:
            if funcionario and dia and presenca:
                registrar_presenca(funcionario, dia, presenca, tabela_selecionada)
                st.success(f"Presença de {funcionario} registrada com sucesso para {dia} na {tabela_selecionada}.")
            else:
                st.error("Por favor, preencha todos os campos.")

    st.markdown("---")  # Separador visual

    # Adicionar Linha Vazia
    st.markdown("### Adicionar Linha Vazia")
    with st.form("adicionar_linha"):
        senha_adicionar = st.text_input("Senha para adicionar linha vazia", type="password")
        if st.form_submit_button("Adicionar Linha Vazia"):
            if senha_adicionar == "  .defcon1 . ":
                registrar_presenca("", None, "", tabela_selecionada)
                st.success("Linha vazia adicionada à tabela.")
            else:
                st.error("Senha incorreta.")

    st.markdown("---")  # Separador visual

    # Listar presenças de todas as tabelas
    st.markdown("### Listar Presenças de Todas as Tabelas")
    for tabela in tabelas:
        if st.button(f"Listar Presenças do {tabela}"):
            presencas_df = listar_presencas(tabela)
            if not presencas_df.empty:
                st.write(f"### Presenças do {tabela}:")
                st.dataframe(presencas_df)
            else:
                st.info(f"A tabela {tabela} não tem registros.")

    st.markdown("---")  # Separador visual

    # Excluir Relatório
    st.markdown("### Excluir Relatório")
    with st.form("excluir_relatorio"):
        senha = st.text_input("Senha para excluir o relatório", type="password")
        if st.form_submit_button("Excluir Relatório"):
            if excluir_relatorio(senha, tabela_selecionada):
                st.success(f"Relatório da {tabela_selecionada} excluído.")
            else:
                st.error("Senha incorreta.")

    # Trancar o aplicativo
    st.markdown("---")  # Separador visual
    st.markdown("### Trancar Aplicativo")
    with st.form("bloquear_app"):
        senha_bloqueio = st.text_input("Senha para trancar o aplicativo", type="password")
        if st.form_submit_button("Trancar"):
            if bloquear_aplicativo(senha_bloqueio):
                st.success("Aplicativo trancado com sucesso.")
            else:
                st.error("Senha incorreta.")
else:
    st.warning("O aplicativo está trancado. Você pode apenas visualizar os relatórios.")

    # Listar presenças de todas as tabelas
    st.markdown("### Visualizar Relatórios")
    for tabela in tabelas:
        if st.button(f"Listar Presenças do {tabela}"):
            presencas_df = listar_presencas(tabela)
            if not presencas_df.empty:
                st.write(f"### Presenças do {tabela}:")
                st.dataframe(presencas_df)
            else:
                st.info(f"A tabela {tabela} não tem registros.")

    # Destrancar o aplicativo
    st.markdown("---")  # Separador visual
    st.markdown("### Destrancar Aplicativo")
    with st.form("desbloquear_app"):
        senha_destrancar = st.text_input("Senha para destrancar o aplicativo", type="password")
        if st.form_submit_button("Destrancar"):
            if destrancar_aplicativo(senha_destrancar):
                st.success("Aplicativo destrancado com sucesso.")
            else:
                st.error("Senha incorreta.")

# Fechar conexão ao sair
conn.close()