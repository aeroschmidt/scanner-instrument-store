# Mantenedora: triagem e Dismiss de Dependabot alerts

Este complemento registra o alerta observado no exercício e um processo de triagem para decisões auditáveis. O alerta é evidência de uma dependência em versão afetada; **Dismiss não corrige nem atualiza a dependência**.

## Resultado observado no exercício

- A lista **Security and quality → Dependabot → Vulnerabilities** mostrou um alerta aberto associado a `junit:junit` no `pom.xml`.
- O detalhe identificou severidade **Moderate**, escopo **Development**, CVE-2020-15250 / GHSA-269g-pwp5-87pp e faixa afetada `>= 4.7, < 4.13.1`.
- O advisory descreve uma exposição local de informações na regra de teste `TemporaryFolder` em sistemas Unix. A condição depende de arquivos temporários sensíveis serem lidos por outros usuários não confiáveis; não é um alerta de execução remota.
- A versão corrigida indicada é 4.13.1. A própria página mostrou que o Dependabot estava criando uma atualização de segurança.
- A mudança demonstrativa foi introduzida como dependência Maven `test`, sem entrar no runtime da aplicação.

[Abrir o alerta observado](https://github.com/schmidt-security-lab/scanner-instrument-store/security/dependabot/1) · [Abrir a lista de Dependabot alerts](https://github.com/schmidt-security-lab/scanner-instrument-store/security/dependabot) · [Abrir o advisory](https://github.com/advisories/GHSA-269g-pwp5-87pp)

## Opções do Dismiss

Na tela do alerta, a pessoa precisa escolher um dos motivos abaixo. A interface também oferece **Dismissal comment**, mas o campo é opcional e tem limite de 280 caracteres.

| Motivo do GitHub | Use quando |
|---|---|
| **A fix has already been started** | Uma correção identificável já está em andamento; vincule PR ou issue. |
| **No bandwidth to fix this** | A correção foi adiada por falta de capacidade; registre responsável e data de reavaliação. |
| **Risk is tolerable to this project** | A equipe revisou evidências e controles e aceitou formalmente o risco. |
| **This alert is inaccurate or incorrect** | Evidências mostram que o alerta não se aplica, por exemplo por versão/faixa incorreta. |
| **Vulnerable code is not actually used** | A parte vulnerável do pacote não é usada; comprove isso. Não selecione apenas porque o pacote está em escopo de teste. |

A escolha do motivo é obrigatória no GitHub; o comentário não é. Portanto, exigir justificativa escrita e aprovação de uma revisora é uma **regra de governança da equipe**, não algo garantido automaticamente pela caixa de Dismiss. O GitHub oferece **delegated alert dismissal** em configurações elegíveis para controlar aprovações; sem essa configuração, a equipe deve seguir seu processo de revisão. Consulte a mantenedora/administradora antes de pressupor que essa trava está ativa.

## Processo recomendado antes de fechar um alerta

1. **Investigar:** confirme pacote, versão resolvida, arquivo, escopo, advisory, severidade, versão corrigida e uso efetivo.
2. **Preferir a correção:** atualize a dependência e valide o build/testes. Se um PR de correção já existe, acompanhe-o em vez de fechar o alerta sem contexto.
3. **Justificar uma exceção:** escolha o motivo que corresponde à evidência. Não use Dismiss apenas para reduzir a lista, deixar checks verdes ou encerrar o trabalho.
4. **Registrar:** apesar de opcional tecnicamente, preencha o comentário conforme a regra recomendada; inclua quem analisou, data, evidências, decisão temporária/permanente, controles compensatórios e acompanhamento. Se o texto exceder 280 caracteres, mantenha o resumo no comentário e registre detalhes em issue/PR ligado ao alerta.
5. **Revisar:** peça aprovação de uma mantenedora ou responsável de segurança antes de concluir o Dismiss, especialmente para risco aceito ou exceção temporária.
6. **Confirmar:** confira se o alerta foi movido para **Closed** e se o motivo/comentário aparecem no registro. O alerta pode ser reaberto se a decisão mudar; a dependência continua precisando de correção quando o risco for real.

### Modelo de comentário (até 280 caracteres)

> Análise: [evidência e por que não corrigir]. Revisado por: [nome], [data]. Decisão: [temporária/permanente]. Mitigação: [controle]. Acompanhamento: [ticket, responsável e prazo se aplicável].

Para decisões temporárias, registre data de reavaliação e trabalho de acompanhamento. Para risco tolerado permanente, registre o aceite e os controles que reduzem a exposição. Não invente prazo quando não houver necessidade; mantenha a data da análise e use prazo apenas quando aplicável.

## Capturas e fontes

A captura da página atual do alerta e a captura do diálogo com as cinco opções foram feitas durante esta sessão de documentação. O diálogo aberto no navegador mostra os rótulos exatos e que comentário é opcional. O repositório não recebeu uma imagem estática dessas telas; os links acima levam ao registro verificável do alerta. Se for necessário arquivar evidência estática para treinamento/auditoria, salve uma captura sem dados sensíveis em `docs/capturas/` e atualize este guia com o arquivo.

- [Documentação oficial: visualizar e atualizar Dependabot alerts](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-dependabot-alerts/view-dependabot-alerts)
- [REST API: propriedades do Dependabot alert, motivo obrigatório e comentário opcional](https://docs.github.com/en/rest/dependabot/alerts)
- [Documentação sobre Dismiss delegado](https://docs.github.com/en/code-security/concepts/security-at-scale/delegated-alert-dismissal)
- [GitHub Advisory Database: CVE-2020-15250](https://github.com/advisories/GHSA-269g-pwp5-87pp)
