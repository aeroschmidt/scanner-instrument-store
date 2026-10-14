# README — entendimento das ferramentas de segurança do GitHub

> Compilado de aprendizado das dúvidas discutidas durante os testes neste repositório. Não é uma política corporativa nem um manual administrativo. O estado citado foi observado em 14 de outubro de 2026 e pode mudar.

## Visão rápida

| Recurso | Para que serve | Abre PR ou bloqueia merge? |
| --- | --- | --- |
| [Dependency graph](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data) | Inventário de bibliotecas e versões identificadas nos manifests e arquivos de lock | Não. É a base para recursos de dependência |
| [Dependabot alerts](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts) | Aponta dependências que correspondem a vulnerabilidades conhecidas | Não, sozinho |
| [Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates) | Propõe atualizar uma dependência vulnerável quando há correção aplicável | Pode abrir PR de correção |
| [Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review) | Analisa dependências adicionadas ou atualizadas por um PR | Pode reprovar um check se o workflow estiver ativo |
| [Code Scanning / CodeQL](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning) | Analisa o código-fonte à procura de padrões vulneráveis | Gera alertas e pode reportar um check |
| [Secret Scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning) | Procura credenciais expostas no repositório | Gera alertas |
| [Push Protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection) | Procura padrões de segredo durante um push | Pode bloquear o push |

## Dependency Graph: de onde vêm os dados?

O GitHub monta o grafo lendo os arquivos de dependências que já estão no repositório. Em Maven, por exemplo, o <code>pom.xml</code> declara dependências diretas. Não é preciso enviar um arquivo separado do grafo. O GitHub pode também identificar dependências indiretas conforme os dados disponíveis para o ecossistema.

O grafo é por repositório. Nos repositórios públicos do GitHub.com fica habilitado por padrão; em privados, depende das configurações e do plano aplicável. A administração pode ser feita em lote para repositórios da organização, mas o grafo é consultado dentro de cada repositório.

Um grafo preenchido não quer dizer que há vulnerabilidade. Ele é o inventário que os alertas e outras ferramentas consultam. Se estiver vazio, verifique se o manifest está na branch padrão e se o ecossistema é reconhecido.

## Dependabot alerts versus Security updates

Quando o grafo encontra uma versão associada a um aviso de segurança conhecido, o GitHub pode criar um **Dependabot alert**. No repositório, ele aparece em **Security and quality > Dependabot > Vulnerabilities**. O detalhe pode mostrar pacote, versões afetadas, severidade, correção disponível e impacto.

O alerta informa sobre um risco; não abre PR nem bloqueia merge por si só.

Com **Dependabot security updates** habilitado, o Dependabot pode abrir um PR quando há alerta e atualização corrigida aplicável. Não é necessariamente um PR por alerta: pode não haver correção, a atualização pode não ser compatível, ou atualizações podem ser agrupadas. O Dependabot automatiza atualizações, mas não substitui a revisão humana do PR.

O arquivo opcional [<code>dependabot.yml</code>](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file) permite personalizar principalmente agendamento e comportamento das atualizações. Security updates podem ser habilitados pelas configurações do GitHub sem esse arquivo.

## Dependency Review: o que entra no PR

Dependency Review examina mudanças de dependências incluídas ou atualizadas pelo PR. A ação oficial roda em um workflow do GitHub Actions e pode usar critérios como severidade ou escopo para determinar se o check falha.

- Um Dependabot alert pode existir porque a branch principal já contém uma dependência vulnerável.
- Dependency Review avalia a diferença de dependências daquele PR; não substitui os alertas.
- Não cria PR de correção. Security updates pode criar.
- O check obrigatório é uma condição de merge configurada separadamente das opções que habilitam alertas.

## Por que o check aparece como “Required” e “skipped”?

<code>Required</code> quer dizer que a regra de proteção espera um check com esse nome. Não garante que a análise foi executada.

Neste repositório, o job **Dependency Review** continua em <code>.github/workflows/dependency-review.yml</code>, mas sua condição faz o job não rodar: <code>if: \${{ false }}</code>. Assim o GitHub Actions o mostra como <code>skipped</code>. A documentação do GitHub explica que um job pulado por condição reporta sucesso e não impede o merge, mesmo quando é obrigatório. Portanto, <code>skipped</code> não significa “analisado e aprovado”.

Isso é diferente de filtros de branch, caminho ou mensagem que impedem o workflow inteiro de iniciar; nesses casos, os checks podem ficar pendentes e bloquear o merge. Veja [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

Para Dependency Review voltar a avaliar mudanças, a condição que pula o job precisa ser removida e o workflow precisa executar. Enquanto ela continuar, a regra pode continuar mostrando o check como esperado, sem haver análise real.

## Como interpretar os checks do PR

A aba **Checks** mostra verificações diferentes:

- O workflow Maven do GitHub Actions compila e executa testes. Build aprovado não significa que o código está livre de vulnerabilidades.
- CodeQL analisa o código-fonte. “No new alerts in code changed by this pull request” quer dizer que não foram encontrados alertas novos nas mudanças do PR; não afirma que o repositório inteiro está sem alertas.
- Dependency Review avalia dependências somente quando o job é executado.
- <code>Required</code> é uma exigência de proteção da branch ou ruleset.

CodeQL pode aparecer em **Checks** sem comentário em **Conversation**, especialmente sem novo achado. Consulte os checks do PR e os alertas na área **Security and quality**.

## Code Scanning, Secret Scanning e Push Protection

Code Scanning/CodeQL analisa código-fonte; Secret Scanning procura credenciais expostas; Push Protection tenta bloquear padrões de segredo no momento do push. São controles diferentes.

Nas telas vistas no estudo, Secret Scanning aparecia desabilitado em uma configuração avançada, enquanto a tela de configuração global mostrava Push Protection com padrões habilitados. Isso não comprova que os alertas de Secret Scanning estejam habilitados naquele repositório: escopo e origem da configuração importam. O GitHub também documenta proteção de push para usuários em alguns contextos públicos. Consulte a documentação de [Push Protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection) para interpretar o estado aplicável.

## Configurações de segurança e regras de merge

Uma configuração avançada controla recursos habilitados para os repositórios aos quais foi aplicada. Dependency graph, Dependabot alerts e Security updates são controles distintos. “Enabled” indica que a função está habilitada naquele escopo; não garante que exista vulnerabilidade, correção ou PR naquele momento.

Rulesets e proteção de branch definem condições de merge, como checks obrigatórios. São separados de habilitar grafo, alertas e atualizações. Uma regra que exige um job sempre pulado não proporciona a revisão indicada pelo nome.

## Exemplo usado nos testes

Em outubro de 2026, um PR de teste adicionou <code>org.apache.commons:commons-compress</code> versão <code>1.25.0</code> com escopo Maven <code>test</code>. O GitHub Advisory Database associa a versão a duas vulnerabilidades moderadas; a versão corrigida indicada é <code>1.26.0</code>:

- [CVE-2024-25710 / GHSA-4g9r-vxhx-9pgx](https://github.com/advisories/GHSA-4g9r-vxhx-9pgx)
- [CVE-2024-26308 / GHSA-4265-ccf5-phj5](https://github.com/advisories/GHSA-4265-ccf5-phj5)

O PR de teste foi mesclado à <code>main</code> para permitir observar o comportamento do Dependabot. A dependência de teste agora faz parte do estado do repositório. O escopo <code>test</code> a mantém fora do runtime normal da aplicação, mas continua sendo dependência do projeto e pode aparecer no grafo e nos alertas. Ao terminar o exercício, remova-a ou atualize para uma versão corrigida e confira os alertas.

Na mesma validação, Dependency Review apareceu como <code>skipped</code> porque o job estava condicionalmente desativado. A leitura atual do ruleset mostrou que ele ainda espera esse nome como check obrigatório; isso não significa que o job tenha analisado o PR.

## Estado observado durante esta compilação

Este retrato pode mudar e não substitui as configurações atuais:

- Na configuração de segurança da organização relatada na conversa, Dependency graph, Dependabot alerts e Security updates apareciam habilitados. Automatic dependency submission, restrição a dismiss direto e Malware alerts estavam como <code>Not set</code>.
- CodeQL/Code Scanning está em **Default setup**, conforme o README do projeto.
- A leitura atual identificou um ruleset **do repositório**, ativo para a branch padrão e com <code>Dependency Review</code> como check obrigatório. Isso é diferente de uma configuração de segurança da organização.
- O workflow Dependency Review está temporariamente pulado pela condição descrita acima.

## Dismiss de alertas

Dismiss encerra um alerta sem necessariamente corrigir a dependência. Os motivos disponíveis incluem correção iniciada, falta de capacidade, risco tolerável, alerta incorreto e código vulnerável não utilizado. A decisão deve ser fundamentada na análise técnica, não usada apenas para limpar a lista ou contornar um check.

Mesmo quando o comentário é opcional na interface, uma prática de governança é registrar justificativa, impacto e, se aplicável, data de revisão. O [guia de mantenedora sobre Dismiss do Dependabot](guia-mantenedora-dependabot-dismissal.md) contém a orientação administrativa detalhada.

## Materiais relacionados

- [Guia de usuário de Dependabot](guia-usuario-dependabot.md)
- [Guia de usuário de Code Scanning](guia-usuario-code-scanning.md)
- [Guia de GitHub Actions e segurança](guia-github-actions-e-seguranca.md)
- [Guia de mantenedora: Dismiss do Dependabot](guia-mantenedora-dependabot-dismissal.md)

## Documentação oficial

- [Dependency graph: reconhecimento de dependências](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data)
- [Dependabot alerts](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts)
- [Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates)
- [Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review)
- [Configurar Dependency Review Action](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-dependency-review-action)
- [Checks obrigatórios: solução de problemas](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
- [Condições de execução no GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)
- [Code Scanning](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning)
- [Secret Scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning)
- [Push Protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)
