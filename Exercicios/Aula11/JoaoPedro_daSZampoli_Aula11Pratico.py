def CalculoProbabilidadeCrossOver(N, Y, P, PrimeiroIndividuo, SegundoIndividuo, IndividuoComparacao):
    Y = int(Y)  # Convertendo Y para inteiro
    
    Filho1 = PrimeiroIndividuo[:Y] + SegundoIndividuo[Y:] # Crossover entre os dois indivíduos (do primeiro até Y do primeiro e do Y até o final do segundo)
    Filho2 = SegundoIndividuo[:Y] + PrimeiroIndividuo[Y:] # Crossover entre os dois indivíduos (do primeiro até Y do segundo e do Y até o final do primeiro)

    ProbabilidadeFilho1 = CalculoProbabilidadeMutacao(Filho1, IndividuoComparacao, P)
    ProbabilidadeFilho2 = CalculoProbabilidadeMutacao(Filho2, IndividuoComparacao, P)

    ProbabilidadeTotal = ProbabilidadeFilho1 + ProbabilidadeFilho2 - (ProbabilidadeFilho1 * ProbabilidadeFilho2)

    return ProbabilidadeTotal


def CalculoProbabilidadeMutacao(Filho, IndividuoComparacao, P):
    Probabilidade = 1.0

    for i in range(len(Filho)):
        if Filho[i] != IndividuoComparacao[i]:
            Probabilidade *= float(P)
        else:
            Probabilidade *= (1 - float(P))
    
    return Probabilidade


def main():
    T = int(input("Digite o número de casos de teste: "))
    for i in range(T):
        N = int(input("Digite a quantidade de bits de cada individuo: "))
        Linha = input("Digite a posição de corte seguida da probabilidade de ocorrência da mutação: ")
        Linha = Linha.split()
        Y = Linha[0]
        P = Linha[1]
        PrimeiroIndividuo = input("Digite o primeiro individuo a ser utilizado no crossover: ")
        SegundoIndividuo = input("Digite o segundo individuo a ser utilizado no crossover: ")
        IndividuoComparacao = input("Digite o indivíduo que será comparado com o resultado do crossover: ")

        Probabilidade = CalculoProbabilidadeCrossOver(N, Y, P, PrimeiroIndividuo, SegundoIndividuo, IndividuoComparacao)
        print(f"Probabilidade de mutação: {Probabilidade:.7f}")

if  __name__ == "__main__":
    main()