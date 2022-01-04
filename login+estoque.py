from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
import sqlite3
import smtplib
import base64

root = Tk()

class Banco_De_Dados():
    ### Classe que possui a funcao de limpar as entrys, as funcoes do Banco de Dados
    ### e a funcao de enviar email quando algum produto estiver com poucas unidades

    def remover(self):
        #Essa função remove (limpa) os valores que estão digitados nas entrys
        self.ent_codigo.delete(0, END)
        self.ent_nomecom.delete(0, END)
        self.ent_nome_gen.delete(0, END)
        self.ent_laboratorio.delete(0, END)
        self.ent_dosagem.delete(0, END)
        self.ent_preco.delete(0, END)
        self.ent_quantidade.delete(0, END)
        self.ent_quantidade_min.delete(0, END)
    def conecta_bd(self):
        #Acesso ao banco de dados
        self.conn = sqlite3.connect("estoque.db")
        self.cursor = self.conn.cursor()
        print("Conectando ao banco de dados")
    def desconecta_bd(self):
        #Fecha o banco de dados
        self.conn.close()
        print("Desconectando o banco de dados")
    def monta_tabela(self):
        self.conecta_bd()
        # Criação das tabelas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                codigo INTEGER PRIMARY KEY,
                nome_comercial CHAR(40) NOT NULL,
                nome_gen CHAR(40),
                laboratorio CHAR(40),
                dosagem INTEGER(10), 
                preco INTEGER(10),
                quantidade INTEGER(10),
                quantidade_min INTEGER(10)
            );
        """)
        self.conn.commit();print("Banco de dados criado")
        self.desconecta_bd()
        
    def variaveis(self):
        #Essa função faz com que as variáveis recebam os valores digitados nas respectivas entries
        self.codigo = self.ent_codigo.get()
        self.nome_comercial = self.ent_nomecom.get()
        self.nome_gen = self.ent_nome_gen.get()
        self.laboratorio = self.ent_laboratorio.get()
        self.dosagem = self.ent_dosagem.get()
        self.preco = self.ent_preco.get()
        self.quantidade = self.ent_quantidade.get()
        self.quantidade_min = self.ent_quantidade_min.get()
    def adicionar_remedio(self):
        #Adiciona as informações de um remédio à listagem.

        self.variaveis() #Recebe os valores digitados nas entrys
        self.conecta_bd() #Acessa o banco de dados

        self.cursor.execute(""" INSERT INTO estoque(nome_comercial, nome_gen, laboratorio, dosagem, preco, 
        quantidade, quantidade_min)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (self.nome_comercial, self.nome_gen, self.laboratorio, self.dosagem,
                             self.preco, self.quantidade, self.quantidade_min))

        self.conn.commit()
        self.desconecta_bd()
        self.select_estoque()
        self.remover() #Limpa as entries após adicionar as informações
    def select_estoque(self):
        self.listagem_estoque.delete(*self.listagem_estoque.get_children())
        self.conecta_bd()
        lista = self.cursor.execute("""SELECT codigo, nome_comercial, nome_gen, laboratorio, dosagem, preco, 
        quantidade, quantidade_min FROM estoque ORDER BY codigo; """)

        for i in lista:
            self.listagem_estoque.insert("", END, values=i)
        self.desconecta_bd()
        self.remover()
    def click_duplo(self, event):
        #Esta função serve para as informações do remédio aparecerem no frame 1 quando o usuário
        #clica duas vezes no remédio na listagem do frame 2.
        self.remover() #Limpa as informações das entrys do frame 1

        for n in self.listagem_estoque.selection():
            col1, col2, col3, col4, col5, col6, col7, col8 = self.listagem_estoque.item(n, "values")
            self.ent_codigo.insert(END, col1)
            self.ent_nomecom.insert(END, col2)
            self.ent_nome_gen.insert(END, col3)
            self.ent_laboratorio.insert(END, col4)
            self.ent_dosagem.insert(END, col5)
            self.ent_preco.insert(END, col6)
            self.ent_quantidade.insert(END, col7)
            self.ent_quantidade_min.insert(END, col8)
    def apagar_remedio(self):
        #Esta função serve para apagar um remédio da listagem do frame 2
        self.variaveis()
        self.conecta_bd()
        self.cursor.execute("""DELETE FROM estoque WHERE codigo = ? """, (self.codigo,),)
        self.conn.commit()
        self.desconecta_bd()
        self.remover()
        self.select_estoque()
    def alterar_remedio(self):
        #Serve para alterar as informações de um remédio que já está cadastrado

        self.variaveis()
        self.conecta_bd()
        self.cursor.execute(""" UPDATE estoque SET nome_comercial = ?, nome_gen = ?, laboratorio = ?, 
        dosagem = ?, preco = ?, quantidade = ?, quantidade_min = ? WHERE codigo = ?""",
                            (self.nome_comercial, self.nome_gen, self.laboratorio, self.dosagem, self.preco,
                             self.quantidade, self.quantidade_min, self.codigo))
        self.conn.commit() #Executa o comando no banco de dados

        ###ENVIANDO E-MAIL###
        try:
            if int(self.quantidade) < int(self.quantidade_min):
                self.enviar_email()
        except:
            pass
        ######################

        self.desconecta_bd()
        self.select_estoque()
        self.remover()
    def buscar_remedio(self):
        self.conecta_bd()
        self.listagem_estoque.delete(*self.listagem_estoque.get_children())
        self.ent_nomecom.insert(END, '%')
        nome = self.ent_nomecom.get()
        self.cursor.execute("""
        SELECT codigo, nome_comercial, nome_gen, laboratorio, dosagem, preco, quantidade, quantidade_min 
        FROM estoque WHERE nome_comercial LIKE '%s' ORDER BY codigo """ % nome)

        busca_nome_comercial = self.cursor.fetchall()

        for i in busca_nome_comercial:
            self.listagem_estoque.insert("", END, values=i)

        self.remover()
        self.desconecta_bd()
    def enviar_email(self):

        # Vai mandar uma notificação por e-mail quando a quantidade de um produto for menor que
        # sua quantidade mínima. ( Essa função é invocada em alterar_remedio() )

        # E-mail que vai mandar a mensagem:
        # emailqueodevquiser@email.com
        # senha: senhaqueodevquiser

        # E-mail que vai receber a mensagem:
        # emailqueodevquiser@email.com
        # senha: senhaqueodevquiser

        self.variaveis()

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('emailqueodevquiser@email.com', 'senhaqueodevquiser@email.com')
            server.sendmail('emailqueodevquiser@email.com', 'emailqueodevquiser@email.com',
                            f'O medicamento {self.nome_comercial} esta em falta no estoque.'
                            f'Verifique o estoque o mais breve possivel.')
        except:
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login('emailqueodevquiser@email.com', 'senhaqueodevquiser@email.com')
                server.sendmail('emailqueodevquiser@email.com', 'emailqueodevquiser@email.com',
                                f'Um medicamento esta em falta no estoque.'
                                f'Verifique o estoque o mais breve possivel.')
            except:
                pass

        print("e-mail enviado")
    def icone64(self):

        # Essa função transforma o ícone do programa em base64.
        # Desse modo, não é necessário colocar a imagem do ícone na mesma pasta do programa.

        self.icone = 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAABeUlEQVRIiWNgGAWjAAnw8fEJmVjZNJhY2' \
                     'TSY2dg1mNnYNcD4IiIiUjSz2MDEosHCI+C/ubv/fwt3//9wtof/fwUNnQaaWaxnYobTYu+g0C3Dz2JRUVEe' \
                     '09rt/7FhUVFRHppYKiAgIODSeeC4w8L3/zHw/Df/XZq3XhQRkZekqqVSCroaTku//ieE7WY8+i+vYWh' \
                     'JNYvdF7/7TozFTku//rfrOfWHKpb+//+fkVhLnZZ+/W/Vd+k/w///jFSz2HPF1/+5u77jxd6rvv' \
                     '636r/8n4GBihZf+/D3/+f///Hih9/+QSympo+vo1n8zEfm/zMvyf+f//2jk8X//v7//O8vwuK/E' \
                     'D6KxdQMapjFz6N0/z/zksTAtLc41uj/M19ZhKW+sv+f+ckN5ziG4ueJ5v+fx5tgt5iaQX3s' \
                     'xR+C2enyu7/Ut5jokovaQT34LaZWWc3AwMDglNE1wbVh3RbXhnVbnOvWbnGuW7sFG9+lbt0' \
                     'Wy5iKCVSxdBQMeQAAQrPZM1U9JBkAAAAASUVORK5CYII=+C/ubv/fwt3//9wtof/fwUNnQaa' \
                     'WaxnYobTYu+g0C3Dz2JRUVEe09rt/7FhUVFRHppYKiAgIODSeeC4w8L3/zHw/Df/XZq3XhQR' \
                     'kZekqqVSCroaTku//ieE7WY8+i+vYWhJNYvdF7/7TozFTku//rfrOfWHKpb+//+fkVhLnZZ+' \
                     '/W/Vd+k/w///jFSz2HPF1/+5u77jxd6rvv636r/8n4GBihZf+/D3/+f///Hih9/+QSympo+vo' \
                     '1n8zEfm/zMvyf+f//2jk8X//v7//O8vwuK/ED6KxdQMapjFz6N0/z/zksTAtLc41uj/M19ZhKW+' \
                     'sv+f+ckN5ziG4ueJ5v+fx5tgt5iaQX3sxR+C2enyu7/Ut5jokovaQT34LaZWWc3AwMDglNE1wbVh' \
                     '3RbXhnVbnOvWbnGuW7sFG9+lbt0Wy5iKCVSxdBQMeQAAQrPZM1U9JBkAAAAASUVORK5CYII='
        self.icone = base64.b64decode(self.icone)
        self.icone = PhotoImage(data=self.icone)

class Tela_Principal(Banco_De_Dados):
    ### Classe que possui todas as configuracoes graficas da tela principal do programa
    def __init__(self):
        self.root = root
        self.icone64()
        self.tela()
        self.frames_da_tela()
        self.widgets_frame_1()
        self.listagem_frame_2()
        self.monta_tabela()
        self.select_estoque()
        root.mainloop()
    def tela(self):
        # Configurações da janela principal do programa
        self.root.title("Estoque Farmácia")

        # Cálculo para a janela abrir um pouco acima do centro da tela
        largura = 800
        altura = 600
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        x = (largura_tela / 2) - (largura / 2)
        y = (altura_tela / 2) - (altura / 2) - 50

        self.root.geometry('%dx%d+%d+%d' % (largura, altura, x, y))
        self.root.wm_iconphoto(True, self.icone)
        self.root.configure(background="#a9a9a9")
        self.root.resizable(False, False)

        barra_menus = Menu(root)
        menu_estoque = Menu(barra_menus, tearoff=0)
        menu_estoque.add_command(label="Sobre", command=self.sobre_equipe)
        barra_menus.add_cascade(label="Mais", menu=menu_estoque)
        root.config(menu=barra_menus)
    def frames_da_tela(self):
        # Criação do frame 1
        self.frame_1 = Frame(self.root, bd=4, bg='#1c1c1c',
                             highlightbackground='#759fe6', highlightthickness=3)
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.46)

        # Criação do frame 2
        self.frame_2 = Frame(self.root, bd=4, bg='#1c1c1c',
                             highlightbackground='#759fe6', highlightthickness=3)
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)
    def widgets_frame_1(self):
        # Nessa função são criados todos os widgets do frame 1.

        # Criação dos botões
        self.bt_buscar = Button(self.frame_1, text="Buscar",bg='#1c1c1c', fg='white',
                                font=('verdana',8,'bold'), bd=2,command=self.buscar_remedio)
        self.bt_buscar.place(relx=0.26,rely=0.05,relwidth=0.13,relheight=0.15)

        self.bt_adicionar = Button(self.frame_1,text="Adicionar",bg='#1c1c1c',
                                   fg='white',font=('verdana',8,'bold'),bd=2,command=self.adicionar_remedio)
        self.bt_adicionar.place(relx=0.6, rely=0.05, relwidth=0.13, relheight=0.15)

        self.bt_alterar = Button(self.frame_1, text="Alterar",bg='#1c1c1c', fg='white',
                                 font=('verdana',8,'bold'), bd=2,command=self.alterar_remedio)
        self.bt_alterar.place(relx=0.73, rely=0.05, relwidth=0.13, relheight=0.15)

        self.bt_apagar = Button(self.frame_1, text="Apagar",bg='#1c1c1c', fg='white',
                                font=('verdana',8,'bold'), bd=2,command=self.apagar_remedio)
        self.bt_apagar.place(relx=0.86, rely=0.05, relwidth=0.13, relheight=0.15)

        # Criação do label
        # coluna1
        self.lb_codigo = Label(self.frame_1,text="Código",font=('verdana', 9),bg='#1c1c1c',fg='white')
        self.lb_codigo.place(relx=0.02, rely=0.001, relwidth=0.13, relheight=0.1)

        self.lb_nome_comercial = Label(self.frame_1,text="Nome Comercial",font=('verdana',9),
                                       bg='#1c1c1c',fg='white')
        self.lb_nome_comercial.place(relx=0.02,rely=0.2,relwidth=0.2,relheight=0.13)

        self.lb_nome_gen = Label(self.frame_1, text="Nome Genérico", font=('verdana', 9),
                                 bg='#1c1c1c', fg='white')
        self.lb_nome_gen.place(relx=0.02, rely=0.4, relwidth=0.2, relheight=0.13)

        self.lb_laboratorio = Label(self.frame_1,text="Laboratório",font=('verdana',9),
                                    bg='#1c1c1c', fg='white')
        self.lb_laboratorio.place(relx=0.02,rely=0.6,relwidth=0.17,relheight=0.13)

        self.lb_dosagem = Label(self.frame_1,text="Dosagem",font=('verdana',9),bg='#1c1c1c',fg='white')
        self.lb_dosagem.place(relx=0.02,rely=0.8,relwidth=0.14,relheight=0.13)

        # coluna2
        self.lb_preco = Label(self.frame_1,text="Preço",font=('verdana',9),bg='#1c1c1c',fg='white')
        self.lb_preco.place(relx=0.5,rely=0.2,relwidth=0.05,relheight=0.13)

        self.lb_quantidade = Label(self.frame_1,text="Quantidade Atual",font=('verdana',9),
                                   bg='#1c1c1c',fg='white')
        self.lb_quantidade.place(relx=0.5,rely=0.4,relwidth=0.15,relheight=0.13)

        self.lb_quantidade_min = Label(self.frame_1,text="Quantidade Mínima",font=('verdana',9),
                                       bg='#1c1c1c', fg='white')
        self.lb_quantidade_min.place(relx=0.5,rely=0.6,relwidth=0.17,relheight=0.13)

        # Criação da entry
        # coluna1
        self.ent_codigo = Entry(self.frame_1, bg='#1c1c1c', fg='white')
        self.ent_codigo.place(relx=0.05, rely=0.1, relwidth=0.2, relheight=0.08)

        self.ent_nomecom = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_nomecom.place(relx=0.05,rely=0.3,relwidth=0.4,relheight=0.08)

        self.ent_nome_gen = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_nome_gen.place(relx=0.05,rely=0.5,relwidth=0.4,relheight=0.08)

        self.ent_laboratorio = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_laboratorio.place(relx=0.05,rely=0.7,relwidth=0.4,relheight=0.08)

        self.ent_dosagem = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_dosagem.place(relx=0.05,rely=0.9,relwidth=0.4,relheight=0.08)

        # coluna2

        self.ent_preco = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_preco.place(relx=0.5,rely=0.3,relwidth=0.4,relheight=0.08)

        self.ent_quantidade = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_quantidade.place(relx=0.5,rely=0.5,relwidth=0.4,relheight=0.08)

        self.ent_quantidade_min = Entry(self.frame_1,bg='#1c1c1c', fg='white')
        self.ent_quantidade_min.place(relx=0.5,rely=0.7,relwidth=0.4,relheight=0.08)
    def listagem_frame_2(self):
        # Nessa função é criada a lista do frame 2 que exibe as informações dos remédios

        # Criação da listagem
        self.listagem_estoque = ttk.Treeview(self.frame_2, height=3, column=("col1", "col2", "col3", "col4",
                                                                             "col5", "col6", "col7", "col8"))
        self.listagem_estoque.place(relx=0.01, rely=0.1, relwidth=0.96, relheight=0.85)
        # Titulo de cada coluna
        self.listagem_estoque.heading("#0", text="")
        self.listagem_estoque.heading("#1", text="Código")
        self.listagem_estoque.heading("#2", text="Nome comercial")
        self.listagem_estoque.heading("#3", text="Nome genérico")
        self.listagem_estoque.heading("#4", text="Laboratório")
        self.listagem_estoque.heading("#5", text="Dosagem")
        self.listagem_estoque.heading("#6", text="Preço")
        self.listagem_estoque.heading("#7", text="Qntd atual")
        self.listagem_estoque.heading("#8", text="Qntd mínima")
        # Largura de cada coluna
        self.listagem_estoque.column("#0", width=1)
        self.listagem_estoque.column("#1", width=25)
        self.listagem_estoque.column("#2", width=65)
        self.listagem_estoque.column("#3", width=65)
        self.listagem_estoque.column("#4", width=65)
        self.listagem_estoque.column("#5", width=25)
        self.listagem_estoque.column("#6", width=25)
        self.listagem_estoque.column("#7", width=25)
        self.listagem_estoque.column("#8", width=25)
        # Barra de rolagem
        self.scrollEstoque = Scrollbar(self.frame_2, orient="vertical")
        self.listagem_estoque.configure(yscroll=self.scrollEstoque.set)
        self.scrollEstoque.place(relx=0.96, rely=0.1, relwidth=0.04, relheight=0.85)
        self.listagem_estoque.bind("<Double-1>", self.click_duplo)
    def sobre_equipe(self):
        #Janela com as informações do trabalho

        janela_sobre = Tk()

        largura = 300
        altura = 200

        largura_tela = janela_sobre.winfo_screenwidth()
        altura_tela = janela_sobre.winfo_screenheight()

        x = (largura_tela / 2) - (largura / 2)
        y = (altura_tela / 2) - (altura / 2) - 50

        janela_sobre.title("Estoque de Farmácia")
        janela_sobre.geometry('%dx%d+%d+%d' % (largura, altura, x, y))
        janela_sobre.configure(bg='#1c1c1c')
        janela_sobre.resizable(False, False)
        texto_sobre = Label(janela_sobre,
                            text="Universidade Estadual da Paraíba\n"
                                 "Trabalho realizado para a disciplina de Algoritmos",
                            bg='#1c1c1c', fg='white',font=('verdana,',9,'bold'))
        texto_sobre.grid(column=0, row=0)

        texto_sobre = Label(janela_sobre, text="Professora: Kézia",
                            bg='#1c1c1c', fg='white',font=('verdana,',9,'bold'))
        texto_sobre.grid(column=0, row=1)

        texto_sobre = Label(janela_sobre,
                            text="Equipe:\n José \n Lucas Manoel \n Maria Eduarda \n Maria Eduarda"
                                 "\n Rayanne",
                            bg='#1c1c1c', fg='white',font=('verdana,',9,'bold'))

        texto_sobre.grid(column=0, row=2)

        #Botão

        bt_sobre = Button(janela_sobre,bg='#1c1c1c',fg='white',text="Ok",command=janela_sobre.destroy)
        bt_sobre.place(relx=0.35,rely=0.8,relwidth=0.3,relheight=0.15)


        janela_sobre.mainloop()

class Tela_Acesso_Cliente(Tela_Principal):
    def __init__(self):
        self.root = root
        self.icone64()
        self.tela_cliente()
        self.frame_do_cliente()
        self.widgets_cliente()
        self.listagem_cliente()
        self.monta_tabela()
        self.select_estoque_cliente()
        root.mainloop()
    def tela_cliente(self):
        # Essa é a tela que aparece para o cliente (ou seja, não precisa logar para acessá-la)
        # Acessada pelo botão "Paciente"

        largura = 602
        altura = 450
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        x = (largura_tela / 2) - (largura / 2)
        y = (altura_tela / 2) - (altura / 2) - 50

        self.root.title("Estoque Farmácia")
        self.root.geometry('%dx%d+%d+%d' % (largura, altura, x, y))
        self.root.wm_iconphoto(True, self.icone)
        self.root.configure(background="#a9a9a9")
        self.root.resizable(False, False)
    def frame_do_cliente(self):
        #Criação do frame da tela do cliente

        self.frame_cliente = Frame(self.root, bd=4, bg='#1c1c1c')
        self.frame_cliente.place(relx=0, rely=0, relwidth=1, relheight=1)
    def widgets_cliente(self):
        #Criação dos widgets da tela do cliente

        # Entry e botão de busca
        self.bt_buscar = Button(self.frame_cliente, text="Buscar",bg='#1c1c1c', fg='white',
                                font=('verdana',8,'bold'), bd=2,command=self.buscar_remedio_cliente)
        self.bt_buscar.place(relx=0.4,rely=0.1,relwidth=0.13,relheight=0.15)

        self.ent_nomecom = Entry(self.frame_cliente,bg='#1c1c1c', fg='white')
        self.ent_nomecom.place(relx=0.05,rely=0.1,relwidth=0.3,relheight=0.07)

        # Botão Voltar (retorna da tela do cliente à tela de login)

        self.bt_voltar = Button(self.frame_cliente,text="Voltar",bg='#1c1c1c',fg='white',
                                font=('verdana',8,'bold'),bd=2,command=self.voltar_login)
        self.bt_voltar.place(relx=0.53,rely=0.1,relwidth=0.13,relheight=0.15)
    def listagem_cliente(self):

        # Criação da listagem
        self.listagem_estoque = ttk.Treeview(self.frame_cliente, height=3, column=("col1","col2","col3","col4",
                                                                             "col5","col6","col7","col8"))
        self.listagem_estoque.place(relx=0.01, rely=0.3, relwidth=0.96, relheight=0.6)
        # Titulo de cada coluna
        self.listagem_estoque.heading("#0", text="")
        self.listagem_estoque.heading("#1", text="Código")
        self.listagem_estoque.heading("#2", text="Nome comercial")
        self.listagem_estoque.heading("#3", text="Nome genérico")
        self.listagem_estoque.heading("#4", text="Laboratório")
        self.listagem_estoque.heading("#5", text="Dosagem")
        self.listagem_estoque.heading("#6", text="Preço")
        self.listagem_estoque.heading("#7", text="Qntd atual")
        self.listagem_estoque.heading("#8", text="Qntd mínima")
        # Largura de cada coluna
        self.listagem_estoque.column("#0", width=1)
        self.listagem_estoque.column("#1", width=25)
        self.listagem_estoque.column("#2", width=65)
        self.listagem_estoque.column("#3", width=65)
        self.listagem_estoque.column("#4", width=65)
        self.listagem_estoque.column("#5", width=25)
        self.listagem_estoque.column("#6", width=25)
        self.listagem_estoque.column("#7", width=25)
        self.listagem_estoque.column("#8", width=25)
        # Barra de rolagem
        self.scrollEstoque = Scrollbar(self.frame_cliente, orient="vertical")
        self.listagem_estoque.configure(yscroll=self.scrollEstoque.set)
        self.scrollEstoque.place(relx=0.96, rely=0.3, relwidth=0.03, relheight=0.6)
        self.listagem_estoque.bind("<Double-1>", self.click_duplo)
    def voltar_login(self):
        #Retorna à tela de login. É o comando do botão 'voltar'
        self.frame_cliente = Frame(self.root, bd=4, bg='#a9a9a9')
        self.frame_cliente.place(relx=0, rely=0, relwidth=1, relheight=1)
        tela_Login()
    def remover_cliente(self):
        #Uma versão da função remover para a tela do cliente
        self.ent_nomecom.delete(0, END)

        # Como a tela do cliente só possui uma entry, estava dando erro ao utilizar a função remover()
        # (que limpa as 8 entries da tela do front end)
    def select_estoque_cliente(self):
        #Uma versão da função select_estoque para a tela do cliente
        # ( usa remover_cliente() em vez de remover() )

        self.listagem_estoque.delete(*self.listagem_estoque.get_children())
        self.conecta_bd()
        lista = self.cursor.execute("""SELECT codigo, nome_comercial, nome_gen, laboratorio, dosagem, preco, 
        quantidade, quantidade_min FROM estoque ORDER BY codigo; """)

        for i in lista:
            self.listagem_estoque.insert("", END, values=i)
        self.desconecta_bd()
        self.remover_cliente()
    def buscar_remedio_cliente(self):
        #Uma versão da função buscar_remedio para a tela do cliente
        # ( usa remover_cliente() em vez de remover() )
        #É invocada no botão "Buscar" da tela do cliente.


        self.conecta_bd()
        self.listagem_estoque.delete(*self.listagem_estoque.get_children())
        self.ent_nomecom.insert(END, '%')
        nome = self.ent_nomecom.get()
        self.cursor.execute("""
                SELECT codigo, nome_comercial, nome_gen, laboratorio, dosagem, preco, quantidade, quantidade_min 
                FROM estoque WHERE nome_comercial LIKE '%s' ORDER BY codigo """ % nome)

        busca_nome_comercial = self.cursor.fetchall()

        for i in busca_nome_comercial:
            self.listagem_estoque.insert("", END, values=i)

        self.remover_cliente()
        self.desconecta_bd()

class tela_Login(Banco_De_Dados):
    def __init__(self):
        self.root = root
        self.icone64()
        self.tela_login()
        self.frames_login()
        self.login_widgets_frame1()
        self.login_widgets_frame2()
        root.mainloop()
    def tela_login(self):
        largura = 602
        altura = 450
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        x = (largura_tela / 2) - (largura / 2)
        y = (altura_tela / 2) - (altura / 2) - 50

        self.root.title("Estoque Farmácia")
        self.root.geometry('%dx%d+%d+%d' % (largura, altura, x, y))
        self.root.configure(background='#a9a9a9')
        self.root.wm_iconphoto(True, self.icone)
        self.root.resizable(False, False)
    def frames_login(self):
        self.frame1 = Frame(self.root, bd=2, bg='#1c1c1c', highlightbackground='#759fe6', highlightthickness=3)
        self.frame1.place(x=30, y=50, height=155, width=545)
        self.frame2 = Frame(self.root, bd=4, bg='#1c1c1c', highlightbackground='#759fe6', highlightthickness=3)
        self.frame2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)
    def login_widgets_frame1(self):
        self.Mensagem = Message(self.frame1, background="#1c1c1c", font="-family {Segoe UI} -size 10",
                                foreground="#ffffff", highlightbackground="#ffffff", highlightcolor="black",
                                text='''  Para verificar se o medicamento desejado está disponível no
            estoque da farmácia, clique no botão abaixo:''',
                                width=460)
        self.Mensagem.place(x=40, y=10, height=83, width=460)

        self.bt_paciente = Button(self.frame1, activebackground="#ececec", activeforeground="#000000",
                                  background="#6894dd", disabledforeground="#a3a3a3",
                                  font="-family {Segoe UI} -size 11", foreground="#000000",
                                  highlightbackground="#d9d9d9", highlightcolor="black",pady="0",
                                  text='''Paciente''',command=self.acesso)
        self.bt_paciente.place(x=220, y=100, height=34, width=107)
    def login_widgets_frame2(self):
        # label e entrada do nome
        self.lb_usu = Label(self.frame2, background="#1c1c1c", disabledforeground="#a3a3a3",
                            font="-family {Segoe UI} -size 11", foreground="#ffffff", text='''E-mail''')
        self.lb_usu.place(x=30, y=20, height=12, width=77)

        self.nomeEntry = Entry(self.frame2, background="#ffffff", disabledforeground="#a3a3a3",
                               font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.nomeEntry.place(x=50, y=40, height=30, width=454)

        # label e entrada da senha
        self.lb_senha = Label(self.frame2, background="#1c1c1c", disabledforeground="#a3a3a3",
                              font="-family {Segoe UI} -size 11", foreground="#ffffff", text='''Senha''')
        self.lb_senha.place(x=40, y=80, height=12, width=57)

        self.senhaEntry = Entry(self.frame2, background="#ffffff", disabledforeground="#a3a3a3",
                                font="TkFixedFont",
                                foreground="#000000", insertbackground="black", show="*")
        self.senhaEntry.place(x=50, y=100, height=30, width=454)

        # botao para o farmaceutico
        self.bt_login = Button(self.frame2, activebackground="#ececec", activeforeground="#000000",
                               background="#6894dd", disabledforeground="#a3a3a3",
                               font="-family {Segoe UI} -size 11",
                               foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", pady="0",
                               text='''Farmacêutico(a)''',command=self.verificaCadastro)
        self.bt_login.place(x=220, y=150, height=34, width=150)
    def erro_login(self):
        #Essa janela vai aparecer quando o usuário digitar as informações de login incorretas
        janela_erro = Tk()

        largura = 260
        altura = 150
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        x = (largura_tela / 2) - (largura / 2)
        y = (altura_tela / 2) - (altura / 2) - 50

        janela_erro.title("Erro")
        janela_erro.geometry('%dx%d+%d+%d' % (largura, altura, x, y))
        janela_erro.configure(bg='#1c1c1c')
        janela_erro.resizable(False, False)

        texto_erro = Label(janela_erro,text="\nInformações de login incorretas.\n\n"
        "Em caso de dúvidas, entre em contato\ncom o administrador do sistema.\n",bg='#1c1c1c',fg='white',
                           font=('verdana',9,'bold'))
        texto_erro.grid(row=0,column=0)

        bt_aceitar_erro = Button(janela_erro,bg='#1c1c1c',fg='white',text="Ok",command=janela_erro.destroy)
        bt_aceitar_erro.place(relx=0.3,rely=0.6,relwidth=0.4,relheight=0.3)

        janela_erro.mainloop()
    def verificaCadastro(self):
        #verifica se o usuário e a senha estão corretos, caso contrário
        #exibe uma mensagem de erro

        usuarioCorreto = "farmaceutico.estoque@gmail.com"
        senhaCorreta = "123456"

        if self.nomeEntry.get() == usuarioCorreto and self.senhaEntry.get() == senhaCorreta:
            print("Usuario logado")
            self.root.quit()
            #daqui abrimos o Tela_Principal()
            Tela_Principal()
        else:
            print("Dados incorretos")
            self.erro_login()
    def acesso(self):
        self.root.quit()
        Tela_Acesso_Cliente()

tela_Login()