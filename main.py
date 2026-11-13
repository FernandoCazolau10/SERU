
import sqlite3
from datetime import datetime, date
import _sqlite3
NOME_BASE_DADOS="sistema.db"
def ligar_base_dados():
    return sqlite3.connect(NOME_BASE_DADOS)
def criar_tabelas():
    with ligar_base_dados() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_registo TEXT UNIQUE,
                nome_completo TEXT NOT NULL,
                data_nascimento TEXT NOT NULL,
                sexo TEXT NOT NULL,
                nif TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                provincia TEXT NOT NULL,
                municipio TEXT NOT NULL,
                bairro TEXT,
                data_registo TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_clinico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utente_id INTEGER NOT NULL,
                data_consulta TEXT NOT NULL,
                servico TEXT NOT NULL,
                diagnostico TEXT NOT NULL,
                observacoes TEXT,
                FOREIGN KEY (utente_id)
                    REFERENCES utentes(id)
            )
        """)
        conexao.commit()

def ler_texto(mensagem, obrigatorio=True):
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("Este campo é obrigatório. Tenta novamente.")
def ler_data_nascimento():
    while True:
        valor = input("Data de nascimento (DD/MM/AAAA): ").strip()
        try:
            data = datetime.strptime(valor, "%d/%m/%Y").date()
            if data > date.today():
                print("A data de nascimento não pode estar no futuro.")
                continue
            return data.strftime("%d/%m/%Y")
        except ValueError:
            print("Data inválida. Exemplo correcto: 15/08/2000.")
def ler_sexo():
    while True:
        print("\nSexo:")
        print("1 - Masculino")
        print("2 - Feminino")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            return "Masculino"
        elif opcao == "2":
            return "Feminino"
        print("Opção inválida.")
def formatar_titulo(titulo):
    print("\n" + "=" * 55)
    print(titulo.center(55))
    print("=" * 55)

def registar_utente():
    formatar_titulo("REGISTO DE NOVO UTENTE")
    nome = ler_texto("Nome completo: ")
    nascimento = ler_data_nascimento()
    sexo = ler_sexo()
    nif = ler_texto(
        "NIF (deixa vazio se não aplicável): ",
        obrigatorio=False
    )
    telefone = ler_texto("Telefone: ", obrigatorio=False)
    email = ler_texto("Correio electrónico: ", obrigatorio=False)
    provincia = ler_texto("Província: ")
    municipio = ler_texto("Município: ")
    bairro = ler_texto("Bairro: ", obrigatorio=False)
    data_registo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        with ligar_base_dados() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO utentes (
                    nome_completo,
                    data_nascimento,
                    sexo,
                    nif,
                    telefone,
                    email,
                    provincia,
                    municipio,
                    bairro,
                    data_registo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome,
                nascimento,
                sexo,
                nif if nif else None,
                telefone,
                email,
                provincia,
                municipio,
                bairro,
                data_registo
            ))
            utente_id = cursor.lastrowid
            numero_registo = f"SREU-{datetime.now().year}-{utente_id:06d}"
            cursor.execute("""
                UPDATE utentes
                SET numero_registo = ?
                WHERE id = ?
            """, (numero_registo, utente_id))
            conexao.commit()
        print("\nUtente registado com sucesso!")
        print(f"Número de registo: {numero_registo}")
        print(f"Nome: {nome}")
    except sqlite3.IntegrityError:
        print("\nErro: o NIF indicado já está associado a outro utente.")
        print("Confirma os dados e tenta novamente.")
    except sqlite3.Error as erro:
        print(f"\nErro ao registar utente: {erro}")

def listar_utentes():
    formatar_titulo("LISTA DE UTENTES")
    try:
        with ligar_base_dados() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT numero_registo, nome_completo,
                       data_nascimento, sexo, telefone
                FROM utentes
                ORDER BY id DESC
            """)
            utentes = cursor.fetchall()
        if not utentes:
            print("Ainda não existem utentes registados.")
            return
        for utente in utentes:
            print("-" * 55)
            print(f"Número: {utente[0]}")
            print(f"Nome: {utente[1]}")
            print(f"Nascimento: {utente[2]}")
            print(f"Sexo: {utente[3]}")
            print(f"Telefone: {utente[4] or 'Não informado'}")
        print("-" * 55)
        print(f"Total de utentes: {len(utentes)}")
    except sqlite3.Error as erro:
        print(f"Erro ao consultar utentes: {erro}")


def pesquisar_utente():
    formatar_titulo("PESQUISAR UTENTE")
    numero = ler_texto("Introduz o número de registo: ").upper()
    try:
        with ligar_base_dados() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT *
                FROM utentes
                WHERE numero_registo = ?
            """, (numero,))
            utente = cursor.fetchone()
        if utente:
            print("\nUTENTE ENCONTRADO")
            print("-" * 55)
            print(f"Número de registo: {utente[1]}")
            print(f"Nome completo: {utente[2]}")
            print(f"Data de nascimento: {utente[3]}")
            print(f"Sexo: {utente[4]}")
            print(f"NIF: {utente[5] or 'Não informado'}")
            print(f"Telefone: {utente[6] or 'Não informado'}")
            print(f"Email: {utente[7] or 'Não informado'}")
            print(f"Província: {utente[8]}")
            print(f"Município: {utente[9]}")
            print(f"Bairro: {utente[10] or 'Não informado'}")
            print(f"Data de registo: {utente[11]}")
        else:
            print("\nNenhum utente encontrado com esse número.")
    except sqlite3.Error as erro:
        print(f"Erro na pesquisa: {erro}")

def registar_consulta():
    formatar_titulo("REGISTAR CONSULTA")
    numero = ler_texto("Número de registo do utente: ").upper()
    try:
        with ligar_base_dados() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome_completo
                FROM utentes
                WHERE numero_registo = ?
            """, (numero,))
            utente = cursor.fetchone()
            if not utente:
                print("\nUtente não encontrado.")
                return
            print(f"\nUtente: {utente[1]}")
            servico = ler_texto("Serviço/Especialidade: ")
            diagnostico = ler_texto("Diagnóstico: ")
            observacoes = ler_texto(
                "Observações clínicas: ",
                obrigatorio=False
            )
            data_consulta = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            cursor.execute("""
                INSERT INTO historico_clinico (
                    utente_id,
                    data_consulta,
                    servico,
                    diagnostico,
                    observacoes
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                utente[0],
                data_consulta,
                servico,
                diagnostico,
                observacoes
            ))
            conexao.commit()
        print("\nConsulta registada com sucesso!")
    except sqlite3.Error as erro:
        print(f"Erro ao registar consulta: {erro}")

def consultar_historico():
    formatar_titulo("HISTÓRICO CLÍNICO")
    numero = ler_texto("Número de registo do utente: ").upper()
    try:
        with ligar_base_dados() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome_completo
                FROM utentes
                WHERE numero_registo = ?
            """, (numero,))
            utente = cursor.fetchone()
            if not utente:
                print("\nUtente não encontrado.")
                return
            print(f"\nNome do utente: {utente[1]}")
            cursor.execute("""
                SELECT data_consulta, servico,
                       diagnostico, observacoes
                FROM historico_clinico
                WHERE utente_id = ?
                ORDER BY id DESC
            """, (utente[0],))
            consultas = cursor.fetchall()
        if not consultas:
            print("Este utente ainda não possui consultas registadas.")
            return
        for indice, consulta in enumerate(consultas, start=1):
            print("\n" + "-" * 55)
            print(f"CONSULTA Nº {indice}")
            print(f"Data: {consulta[0]}")
            print(f"Serviço: {consulta[1]}")
            print(f"Diagnóstico: {consulta[2]}")
            print(f"Observações: {consulta[3] or 'Sem observações'}")
        print("\n" + "-" * 55)
    except sqlite3.Error as erro:
        print(f"Erro ao consultar histórico: {erro}")

def menu_principal():
    while True:
        formatar_titulo("SREU - SISTEMA DE REGISTO ELETRÓNICO DE UTENTES")
        print("1 - Registar novo utente")
        print("2 - Listar todos os utentes")
        print("3 - Pesquisar utente")
        print("4 - Registar consulta")
        print("5 - Consultar histórico clínico")
        print("0 - Sair do sistema")
        print("=" * 55)
        opcao = input("Seleccione uma opção: ").strip()
        if opcao == "1":
            registar_utente()
        elif opcao == "2":
            listar_utentes()
        elif opcao == "3":
            pesquisar_utente()
        elif opcao == "4":
            registar_consulta()
        elif opcao == "5":
            consultar_historico()
        elif opcao == "0":
            print("\nA encerrar o SREU...")
            print("Obrigado por utilizar o sistema!")
            break
        else:
            print("\nOpção inválida. Escolhe uma opção do menu.")
        input("\nPressiona ENTER para continuar...")



if __name__ == "__main__":
    criar_tabelas()
    menu_principal()