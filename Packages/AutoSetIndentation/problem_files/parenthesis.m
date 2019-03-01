// https://github.com/SublimeTextIssues/Core/issues/1459
// Guess settings from buffer: Detected as Space/2 but should be Space/4

function x = my_roots( coeficientes_do_polinomio )

    passo_atual_de_iteracao = 1;
    grau_do_polinomio       = length( coeficientes_do_polinomio ) - 1

    # Salvamos o valor original do polinômio para o processo de purificação.
    polinomio_original         = coeficientes_do_polinomio
    grau_do_polinomio_original = grau_do_polinomio

    while grau_do_polinomio > 0

        xi( passo_atual_de_iteracao ) = fLocaliza( grau_do_polinomio, coeficientes_do_polinomio )

        [ x(passo_atual_de_iteracao), M(passo_atual_de_iteracao) ] = fNewtonPolinomios( grau_do_polinomio, coeficientes_do_polinomio, )

        # Redução de grau pela raiz x, M vezes.
        # Criar um função de redução de grau, que receba retorne o novo para continuar o processo.
        [ grau_do_polinomio, coeficientes_do_polinomio ] = reduzirGrauDoPolinomio(
                                                                                   grau_do_polinomio,
                                                                                   coeficientes_do_polinomio,
                                                                                   x( passo_atual_de_iteracao ),
                                                                                   M( passo_atual_de_iteracao )
                                                                                 )

    end
end
