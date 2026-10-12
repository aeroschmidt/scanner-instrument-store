# Guia do usuário para Code Scanning em Pull Requests

Este guia é para pessoas que abrem ou revisam Pull Requests. Ele mostra como localizar um resultado do Code Scanning, entender o que o alerta está dizendo e decidir o próximo passo. A equipe que mantém o repositório configura a ferramenta; este guia trata do trabalho de quem contribui com código.

> **Leitura importante das capturas:** as telas abaixo são exemplos de treinamento para explicar a interface do GitHub. Uma delas mostra uma vulnerabilidade intencional em um exercício isolado. Não replique esse código em um projeto real. A aparência e os nomes dos botões podem variar conforme as configurações do repositório.

## 1. O que o Code Scanning faz

Code Scanning analisa o código-fonte em busca de padrões de falha e vulnerabilidade. Com CodeQL, o GitHub executa consultas de análise estática e pode relacionar um dado de entrada à operação que o utiliza. Quando encontra algo, pode registrar um alerta com regra, severidade, arquivo e localização.

O alerta é uma indicação para revisão. Leia os detalhes no contexto do código antes de decidir. Um resultado sem alertas significa que a análise executada não relatou um achado reconhecido; não prova que todo o código está seguro.

## 2. Onde o resultado aparece

### No Pull Request

A seção **Checks** informa se a análise terminou e se o check passou. Alguns checks de Code Scanning também mostram a quantidade de novos alertas e anotações na alteração.

![Exemplo de check de CodeQL no PR com uma descoberta de severidade alta](codeql-learning-materials/.github/images/dismissal-pr-checks.png)

Essa tela mostra um check de segurança que encontrou um alerta. Isso é diferente de uma falha de compilação ou teste: abra o check correspondente e leia o resumo para saber qual etapa terminou em falha e por quê. Um alerta pode ser encontrado mesmo se o build Maven ou outra suíte de testes passar.

### Na área de segurança do repositório

A lista de **Security and quality → Code scanning** reúne alertas do repositório. Abra o alerta para ver a severidade, a regra e a localização.

![Exemplo da lista Code Scanning com um alerta aberto](codeql-learning-materials/.github/images/dismissal-alert-list.png)

### Nos detalhes do alerta

A página do alerta pode destacar linhas do código, indicar a regra e oferecer informações adicionais, como o caminho dos dados. Use esses detalhes para entender de onde vem o dado e onde ele é usado.

![Exemplo dos detalhes do alerta, incluindo localização e ação Dismiss alert](codeql-learning-materials/.github/images/dismissal-alert-detail.png)

## 3. Como investigar um alerta

1. Abra o alerta a partir do PR ou da lista **Code scanning**.
2. Leia o título, a descrição da regra e a severidade.
3. Verifique o arquivo e as linhas indicadas. Leia o código ao redor e o diff completo do PR.
4. Se houver **Show paths** ou visualização de fluxo de dados, siga a origem da entrada e o ponto onde ela é utilizada.
5. Compare o achado com o comportamento real da alteração. Considere validações, sanitização, permissões e outros controles presentes no código.
6. Se não souber avaliar o risco, peça ajuda ao revisor ou à equipe responsável pela segurança antes de fechar o alerta.

Uma recomendação automática é um ponto de partida. Confirme que ela se aplica ao contexto antes de alterar o código.

## 4. Resposta preferida: corrigir o código

Quando o alerta é válido, corrija a causa no código. Faça a alteração em uma branch, inclua ou ajuste testes quando apropriado, atualize o PR e aguarde uma nova execução do Code Scanning.

Depois da nova análise, volte aos detalhes do alerta. Confirme se foi corrigido ou se ainda existe uma instância aberta. A correção deve remover o risco; não basta esconder o alerta.

## 5. Quando usar Dismiss

Use **Dismiss** somente depois de examinar o alerta e concluir que não é necessária uma alteração no código. Exemplos possíveis incluem um falso positivo confirmado, código limitado a testes ou um risco que a equipe analisou e decidiu aceitar. Siga sempre a política de segurança e as permissões do repositório.

1. Abra o alerta e verifique sua descrição, localização, severidade e fluxo de dados.
2. Selecione **Dismiss alert** e escolha o motivo que corresponde à análise.
3. Registre um comentário claro com a justificativa e o contexto necessário.
4. Confirme o Dismiss e verifique se o alerta aparece na lista **Closed** com o motivo e comentário esperados.

A lista de motivos disponível pode variar de acordo com a ferramenta e a interface.

![Exemplo das opções de motivo para Dismiss](codeql-learning-materials/.github/images/dismiss-alert-options.png)

A imagem seguinte ilustra que o evento e a justificativa ficam registrados na timeline do alerta.

![Exemplo de registro de Dismiss na timeline de auditoria](codeql-learning-materials/.github/images/audit-log-alert-dismissed.png)

### O que o Dismiss muda

O Dismiss altera o estado do alerta, mas não corrige o código. De acordo com a documentação do GitHub, o Dismiss se aplica a todos os branches, remove o alerta da contagem atual de alertas abertos e o move para **Closed**, onde pode ser reaberto. O motivo fica registrado e o comentário opcional aparece na timeline. Na próxima análise, o mesmo código não gera o mesmo alerta. A escolha do motivo também pode influenciar se a consulta continuará incluída em análises futuras.

**Não use Dismiss para deixar o check verde.** Se o risco for real, corrija o código. Se a equipe aceitar a exceção, registre uma justificativa que possa ser entendida em uma revisão ou auditoria futura.

### Modelo de comentário para Dismiss

Adapte este exemplo à decisão aprovada pela equipe:

> Revisado por [pessoa/equipe] em [data]. Motivo: [motivo do Dismiss]. O alerta não exige alteração de código porque [evidências]. A decisão é [temporária/permanente]. Controle ou acompanhamento: [ação], responsável [pessoa/equipe], prazo [data].

Registre também se a decisão foi revisada por outra pessoa. Se for temporária, inclua um prazo e uma tarefa de acompanhamento.

### Aprovação delegada

Algumas organizações podem configurar **delegated alert dismissal** para exigir revisão antes de concluir certos Dismiss. Se a interface pedir uma solicitação de aprovação, explique o motivo e aguarde a decisão da pessoa autorizada. Não tente contornar essa etapa.

## 6. Diferenças que evitam confusão

| O que você vê | O que significa | Próxima ação |
|---|---|---|
| Code Scanning está em execução | A análise ainda não terminou | Aguarde e depois leia o resultado |
| Code Scanning reporta um alerta | A ferramenta identificou um padrão que precisa ser revisado | Abra o alerta e avalie o código |
| Build ou testes falham | A compilação ou uma etapa de teste não passou | Abra o job que falhou e investigue o log |
| Check de Code Scanning falha | Pode haver alertas novos ou outra condição de segurança configurada | Leia o resumo do check e os alertas |
| Não há alerta novo no PR | A análise executada não reportou novos achados para as mudanças verificadas | Confira se a análise rodou e se cobre a linguagem e o código |
| Alerta em Closed | O alerta foi corrigido ou recebeu Dismiss | Abra a timeline para confirmar como foi resolvido |

Um check vermelho não significa necessariamente que os testes de aplicação falharam. Da mesma forma, um check verde não substitui a revisão do diff nem garante ausência de vulnerabilidades.

## 7. Checklist para autores e revisores

### Antes de pedir revisão

- [ ] Li os checks e confirmei quais tarefas realmente foram executadas.
- [ ] Investiguei cada alerta novo e conferi o trecho no contexto do diff.
- [ ] Corrigi os achados válidos ou pedi triagem à equipe responsável.
- [ ] Para qualquer Dismiss, registrei o motivo e o contexto conforme a política da equipe.
- [ ] Não incluí credenciais ou dados reais de clientes em exemplos.

### Durante a revisão

- [ ] O diff corresponde ao objetivo descrito no PR.
- [ ] Entendi os alertas e as falhas de build ou teste separadamente.
- [ ] A justificativa de cada Dismiss tem evidência suficiente e responsável identificável.
- [ ] A aprovação segue as regras do repositório; checks automáticos não substituem aprovação humana.

## 8. Referências oficiais

- [Resolver alertas de Code Scanning](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)
- [Fazer triagem de alertas em Pull Requests](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/triage-alerts-in-pull-requests)
- [Dismiss delegado de alertas](https://docs.github.com/en/code-security/concepts/security-at-scale/delegated-alert-dismissal)
- [Sobre alertas do Code Scanning](https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning-alerts)
