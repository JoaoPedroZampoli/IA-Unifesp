import random
import numpy as np

Direcao = ["N", "S", "L", "O"]
Movimento = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}

class Mundo:
    def __init__(self):
        self.tamanho = 4
        self.mapa = np.full((self.tamanho, self.tamanho), "", dtype=object)
        self.visao = np.full((self.tamanho, self.tamanho), "", dtype=object)
        self.celulas_visitadas = np.zeros((self.tamanho, self.tamanho), dtype=bool)
        self.jogador = (0, 0)
        self.direcao = "L"
        self.flecha = True
        self.ouro = False
        self.ouroPego = False
        self.Wumpusvivo = True
        self.pontos = 0
        self.grito = False
        self.morto = False

        self.DisporMapa()
        self.celulas_visitadas[0][0] = True

    def DisporMapa(self):
        self.WumpusPos = self.RandPos(Ocupado = [(0, 0)])
        self.AdicionarPercepcao(self.WumpusPos, "Fedor", Adjacencia = True)
        self.mapa[self.WumpusPos[0]][self.WumpusPos[1]] = "W"

        self.abismos = []
        for i in range(3):
            AbismoPos = self.RandPos(Ocupado = [self.WumpusPos, (0, 0)] + self.abismos)
            self.abismos.append(AbismoPos)
            self.AdicionarPercepcao(AbismoPos, "Brisa", Adjacencia = True)
            self.mapa[AbismoPos[0]][AbismoPos[1]] += "A"

        self.OuroPos = self.RandPos(Ocupado = [self.WumpusPos, (0, 0)] + self.abismos)
        self.AdicionarPercepcao(self.OuroPos, "Brilho")
        self.mapa[self.OuroPos[0]][self.OuroPos[1]] = "O"

    def RandPos(self, Ocupado):
        while True:
            Posicao = [random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)]
            if tuple(Posicao) not in [tuple(pos) for pos in Ocupado]:
                return tuple(Posicao)

    def AdicionarPercepcao(self, Posicao, Percepcao, Adjacencia = False):
        if Adjacencia:
            for direcaoX, direcaoY in Movimento.values():
                x, y = Posicao[0] + direcaoX, Posicao[1] + direcaoY
                if 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                    if isinstance(self.visao[x][y], str):
                        if self.visao[x][y]:
                            self.visao[x][y] += f", {Percepcao}"
                        else:
                            self.visao[x][y] = Percepcao
        else:
            # Adiciona percepção diretamente na posição (não adjacente)
            if isinstance(self.visao[Posicao[0]][Posicao[1]], str):
                if self.visao[Posicao[0]][Posicao[1]]:
                    self.visao[Posicao[0]][Posicao[1]] += f", {Percepcao}"
                else:
                    self.visao[Posicao[0]][Posicao[1]] = Percepcao
    
    def EstadoAtual(self):
        x, y = self.jogador
        estadoAtual = f"Posição do Jogador: {x}, {y}\n Direção: {self.direcao}\n"
        if self.flecha:
            estadoAtual += "Possui uma flecha\n"
        else:
            estadoAtual += "Flecha Já usada\n"
        if self.grito:
            estadoAtual += "Você ouviu um grito\n"
            self.grito = False  # Reset o grito após ser percebido
        if self.ouroPego:
            estadoAtual += "Você está carregando o ouro\n"
        Visao = self.visao[x][y]
        if Visao:
            estadoAtual += f"Você percebeu: {Visao}\n"
        else:
            estadoAtual += "Você não percebeu nada\n"
        print(estadoAtual)
        self.MostrarMapa()

    def MostrarMapa(self):
        mapa_visual = []
        for i in range(self.tamanho):
            linha = []
            for j in range(self.tamanho):
                if (i, j) == self.jogador:
                    linha.append("J")  # Jogador
                elif self.celulas_visitadas[i][j]:
                    if self.mapa[i][j]:
                        linha.append(self.mapa[i][j])  # Conteúdo conhecido
                    else:
                        linha.append(".")  # Célula vazia visitada
                else:
                    linha.append("?")  # Célula não visitada
            mapa_visual.append(linha)
        
        print("\nMapa do Jogo:")
        for linha in mapa_visual:
            print(" ".join(linha))
        print()

    def DirecaoJogador(self, NovaDirecao):
        self.direcao = NovaDirecao
        print(f"Você virou para {self.direcao}")

    def MoverJogador(self):
        direcaoX, direcaoY = Movimento[self.direcao]
        novoX, novoY = self.jogador[0] + direcaoX, self.jogador[1] + direcaoY

        if 0 <= novoX < self.tamanho and 0 <= novoY < self.tamanho:
           self.jogador = (novoX, novoY)
           self.celulas_visitadas[novoX][novoY] = True
           Conteudo = self.mapa[novoX][novoY]
           if "W" in Conteudo and self.Wumpusvivo:
               self.morto = True
               self.pontos -= 100
               print("Você foi comido pelo Wumpus!")
           elif "A" in Conteudo:
               self.morto = True
               self.pontos -= 100
               print("Você caiu em um abismo!")
           elif "O" in Conteudo and not self.ouroPego:
               self.ouro = True
               print("Você encontrou o ouro!")
           else:
               self.pontos -= 1
        else:
            print("Ai! Você bateu em uma parede!")
            self.pontos -= 1
    
    def AtirarFlecha(self):
        if self.flecha:
            self.flecha = False
            self.pontos -= 10  # Penalidade por usar a flecha
            x, y = self.jogador
            atingiu_algo = False
            
            while not atingiu_algo:
                x += Movimento[self.direcao][0]
                y += Movimento[self.direcao][1]
                
                if 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                    if (x, y) == self.WumpusPos and self.Wumpusvivo:
                        self.Wumpusvivo = False
                        self.grito = True
                        self.mapa[x][y] = ""  # Remove o Wumpus do mapa
                        print("Você acertou o Wumpus!")
                        atingiu_algo = True
                    elif (x, y) in self.abismos:
                        print("Sua flecha caiu em um abismo!")
                        atingiu_algo = True
                else:
                    print("Sua flecha atingiu a parede!")
                    atingiu_algo = True
                    
            if not atingiu_algo:
                print("Você atirou a flecha... mas não acertou nada!")
        else:
            print("Você não tem mais flechas!")
            return False
        
    def PegarOuro(self):
        if self.jogador == self.OuroPos and self.ouro == True:
            self.ouroPego = True
            self.ouro = False
            # Removendo o ouro do mapa
            self.mapa[self.OuroPos[0]][self.OuroPos[1]] = ""
            print("Você pegou o ouro!")
        else:
            print("Não há ouro aqui!")
        
    def Escalar(self):
        if self.jogador == (0, 0):
            if self.ouroPego:
                self.pontos += 1000  # Prêmio maior por levar o ouro
                print("Você ganhou!")
                print(f"Você fez {self.pontos} pontos!")
            else:
                print("Você não tem ouro!")
                print(f"Você escapou sem o ouro. Pontuação: {self.pontos}")
            exit()
        else:
            print("Você não pode escalar aqui!")

def IniciarJogo():
  mundoGerado = Mundo()
  print("Bem-vindo ao Mundo de Wumpus!")
  mundoGerado.EstadoAtual()

  while not mundoGerado.morto:
    print("Escolha uma ação:")
    print("1. Mover")
    print("2. Virar o jogador")
    print("3. Atirar flecha")
    print("4. Pegar ouro")
    print("5. Escalar")
    acao = input("Digite o número da ação: ")

    if acao == "1":
        mundoGerado.MoverJogador()
    elif acao == "2":
        direcao = input("Digite a direção (L, O, N, S): ").upper()
        if direcao in Direcao:
            mundoGerado.DirecaoJogador(direcao)
        else:
            print("Direção inválida! Tente novamente.")
    elif acao == "3":
        mundoGerado.AtirarFlecha()
    elif acao == "4":
        mundoGerado.PegarOuro()
    elif acao == "5":
        mundoGerado.Escalar()
    else:
        print("Ação inválida! Tente novamente.")
    
    if not mundoGerado.morto:
        mundoGerado.EstadoAtual()

if __name__ == "__main__":
  IniciarJogo()