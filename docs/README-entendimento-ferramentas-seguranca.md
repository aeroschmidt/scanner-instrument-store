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

No teste com Commons Compress, havia duas vulnerabilidades no mesmo pacote, corrigidas pela versão 1.26.0. O Dependabot abriu automaticamente um único PR que atualiza o pacote de 1.25.0 para 1.26.0 e cobre as duas vulnerabilidades. Na tela do alerta, **Review security update** abre o PR que já existe; não dispara uma análise nem cria um segundo PR. O GitHub explica esse fluxo no [Dependabot quickstart](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/dependabot-quickstart) e em [Dependabot pull requests](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/supply-chain-security/dependabot-pull-requests).

Por padrão, os PRs do Dependabot são criados sem reviewers. A exigência de aprovação vem da proteção da branch (branch protection ou ruleset), não do Dependabot: se a regra exigir uma ou mais aprovações, o merge fica bloqueado até o número exigido de pessoas elegíveis aprovar. No repositório de teste, a regra consultada exige zero aprovações; a mensagem vista no repositório da empresa indica uma política diferente, que exige pelo menos uma aprovação de alguém com acesso de escrita. O GitHub documenta as [revisões obrigatórias em branches protegidas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) e como adicionar reviewers a PRs do Dependabot por meio de [CODEOWNERS](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/customizing-dependabot-security-prs).

O arquivo opcional [<code>dependabot.yml</code>](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file) permite personalizar principalmente agendamento e comportamento das atualizações. Security updates podem ser habilitados pelas configurações do GitHub sem esse arquivo.

## Dependency Review: o que entra no PR

Dependency Review examina mudanças de dependências incluídas ou atualizadas pelo PR. A ação oficial roda em um workflow do GitHub Actions e pode usar critérios como severidade ou escopo para determinar se o check falha.

- Um Dependabot alert pode existir porque a branch principal já contém uma dependência vulnerável.
- Dependency Review avalia a diferença de dependências daquele PR; não substitui os alertas.
- Não cria PR de correção. Security updates pode criar.
- O check obrigatório é uma condição de merge configurada separadamente das opções que habilitam alertas.

## Por que o check aparece como “Required” e “skipped”?

<code>Required</code> quer dizer que a regra de proteção espera um check com esse nome. Não garante que a análise foi executada.

Neste repositório, o job **Dependency Review** continua em <code>.github/workflows/dependency-review.yml</code>, mas a condição do job está configurada para sempre avaliar como falsa. Assim o GitHub Actions o mostra como <code>skipped</code>. A documentação do GitHub explica que um job pulado por condição reporta sucesso e não impede o merge, mesmo quando é obrigatório. Portanto, <code>skipped</code> não significa “analisado e aprovado”.

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

### Resultado do teste de push local

Em 14/10/2026, ao tentar enviar a branch de teste `test/secret-scanning-push-protection`, o GitHub rejeitou o push com `GH013` / **GITHUB PUSH PROTECTION**. A mensagem apontou um segredo detectado em `secret-scanning-test.txt` no commit `6d9d65b`. A branch remota permaneceu no commit-base (`bb049eb`), então a alteração continuou apenas local e nenhum PR pôde ser aberto.

Na inspeção de 14/10/2026, **Push protection** aparecia como **Disabled** em Settings > Advanced Security do repositório, após alteração da configuração da organização. Uma tentativa anterior ainda foi rejeitada com `GH013`; depois, um novo push do mesmo commit foi aceito e um PR demonstrativo foi aberto para observar o comportamento do Secret Scanning. O botão **Push protection for yourself** aparecia ativo quando a conta foi inspecionada; por isso, não atribuir o resultado final a uma única camada sem conferir o estado efetivo no próximo teste. Consulte [Push protection para usuários](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/manage-user-push-protection) e [alertas do Secret Scanning](https://docs.github.com/en/code-security/concepts/secret-security/about-alerts).

Na repetição do teste, uma branch nova com o mesmo tipo de valor sintético foi aceita pelo push e gerou o PR demonstrativo [#38](https://github.com/schmidt-security-lab/scanner-instrument-store/pull/38), que foi fechado sem merge. Isso confirma que esse valor de teste não foi bloqueado nessa tentativa; o estado do alerta de Secret Scanning ainda precisa ser conferido na área de segurança do repositório. Fechar o PR não apaga o commit, o arquivo nem a branch remota, então o alerta pode continuar aberto até remover o conteúdo detectado ou resolver o alerta.

Após o fechamento do PR #38, a pessoa usuária informou que o alerta ainda visível em Secret Scanning era do PR de teste anterior. O alerta é associado ao segredo detectado no repositório, não ao estado do PR; fechar PRs não remove commits nem arquivos que permanecem em branches remotas. O arquivo/localização exata do alerta não foi confirmado nesta conversa.

Mesmo removendo o valor do arquivo atual, o alerta do Secret Scanning não é fechado automaticamente. O GitHub verifica o histórico de Git em todas as branches e orienta encerrar manualmente o alerta depois de corrigir ou confirmar o caso. Para o token fictício de treinamento, confirme a localização e, se for de fato esse teste, feche como **Used in tests** com um comentário curto. Veja [como resolver alertas](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/resolving-alerts) e [o escopo da varredura](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning).

A captura posterior mostrou **Generic patterns: Disabled**. Essa opção controla a detecção de segredos genéricos, como chaves privadas e strings de conexão. No teste observado, após desabilitá-la o push do token fictício foi aceito; portanto, para esse valor de treinamento, a detecção associada a **Generic patterns** era necessária para acionar o bloqueio. Isso não transforma essa opção no controle geral da proteção de push: o resultado observado vale para esse padrão e essa configuração. Consulte [o exercício oficial com o token fictício](https://docs.github.com/pt/get-started/learning-to-code/storing-your-secrets-safely) e [a documentação de padrões genéricos](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enabling-secret-scanning-for-generic-patterns).

### Proteção ativa não significa bloquear qualquer token

Mesmo ativa, a proteção contra push bloqueia somente segredos compatíveis com padrões reconhecidos e cobertos por push protection. Alguns padrões geram alertas, mas não são bloqueados; versões antigas de tokens também podem ficar fora da detecção. O GitHub recomenda consultar a tabela de [padrões compatíveis](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns) e os [limites de detecção](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-scope). No teste deste repositório, o valor sintético foi bloqueado em uma tentativa anterior e o mesmo commit passou após mudanças na configuração; isso confirma mudança no estado efetivo da proteção, não uma regra geral de que tokens passam.

### Exceções sem desligar Push Protection

Não há uma lista simples para permitir silenciosamente um único valor de token e continuar bloqueando todos os outros do mesmo padrão. Para um caso isolado, pode-se usar o bypass da tentativa bloqueada; a escolha do motivo influencia o alerta. Para excluir um arquivo ou diretório inteiro, `.github/secret_scanning.yml` aceita `paths-ignore`, mas isso remove esse caminho da detecção do Secret Scanning e do Push Protection, então não serve para demonstrar um alerta nesse arquivo. A isenção de atores confiáveis ignora a proteção para todos os pushes deles e é ampla; use com cautela. Veja [exclusões de caminhos](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/customize-leak-detection/exclude-folders-and-files), [bypass delegado](https://docs.github.com/en/code-security/concepts/secret-security/delegated-bypass) e [alertas ao fazer bypass](https://docs.github.com/en/code-security/concepts/secret-security/push-protection).

Guardar uma chave em **Settings > Secrets and variables > Actions** não cria uma exceção para Secret Scanning nem para Push Protection. O armazenamento de Actions fornece valores a workflows; se o valor real for copiado para um arquivo ou commit, ele ainda poderá ser detectado e bloqueado. A prática correta é referenciar o segredo pelo contexto `secrets` no workflow e nunca gravar seu valor literal no repositório. Veja [Secrets do GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions).

### Bypass delegado pela organização

Sim. Uma organização pode configurar o **bypass delegado**: definir pessoas, equipes ou funções autorizadas e exigir que revisores aprovem pedidos dos demais colaboradores. A configuração fica em **Organization Settings > Security > Advanced Security > Configurations**, dentro de uma configuração de segurança aplicada aos repositórios; nela, Push Protection precisa estar **Enabled** e os privilégios de bypass devem ser definidos. O recurso para repositórios de organização exige **GitHub Team com GitHub Secret Protection** ou GitHub Enterprise. Como a organização deste estudo foi identificada anteriormente como Free, esse bypass delegado não está disponível no plano atual. Além disso, na captura mais recente Push Protection estava **Disabled**, então não havia bloqueio organizacional ativo para contornar. A proteção pessoal da conta é uma camada separada e não é administrada pelo bypass da organização. Consulte [requisitos e funcionamento do bypass delegado](https://docs.github.com/en/code-security/concepts/secret-security/delegated-bypass) e [como habilitá-lo na organização](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/manage-bypass-requests/enable-delegated-bypass).

### Aviso no PR sem bloquear

Os alertas nativos do Secret Scanning ficam em **Security and quality > Secret scanning**; não há garantia de comentário ou aviso inline na conversa do PR. Para exibir um aviso durante a revisão sem barrar push ou merge, é necessário um workflow de PR com uma ferramenta de detecção que publique um resumo, anotação ou comentário informativo. Esse check não deve ser marcado como obrigatório nem falhar o workflow. Consulte [como visualizar alertas do Secret Scanning](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/viewing-alerts) e [notificações de alertas](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/monitoring-alerts). A regra nativa de ruleset para exigir alertas resolvidos é bloqueante, portanto não atende ao requisito de apenas avisar: [detalhes da regra](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/block-merges-with-secrets).

Para demonstrar uma vulnerabilidade diretamente na conversa do PR com a ferramenta nativa, uma alternativa é adicionar, em branch de teste, um exemplo Java isolado de SQL injection e deixar o CodeQL analisar o PR. O alerta pode aparecer como anotação na aba Conversation e em Files changed se o trecho vulnerável estiver no diff. Isso demonstra **Code Scanning/CodeQL**, não Secret Scanning. Para que seja apenas aviso, o check CodeQL não pode estar configurado como obrigatório no ruleset; a regra que exige alertas de segredo resolvidos é bloqueante e requer GitHub Team com Secret Protection ou Enterprise. Veja [alertas do CodeQL em PRs](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/triage-alerts-in-pull-requests) e [requisitos da regra de Secret Scanning](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/block-merges-with-secrets).

Para o teste solicitado, foi preparado um workflow separado de GitHub Actions que procura no diff do PR uma linha de treinamento marcada como `GH_TOKEN` e publica um comentário informativo, sem reproduzir o valor. Ele não valida se o valor é um segredo real e não cria um alerta nativo do Secret Scanning; apenas demonstra como uma mensagem pode aparecer na conversa do PR. O job não falha nem bloqueia o merge e não deve ser marcado como check obrigatório. O PR de demonstração deve permanecer sem merge e ser encerrado/removido após a avaliação. Consulte [eventos de pull request no GitHub Actions](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request) e [permissões do `GITHUB_TOKEN`](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication).

## Configurações de segurança e regras de merge

Uma configuração avançada controla recursos habilitados para os repositórios aos quais foi aplicada. Dependency graph, Dependabot alerts e Security updates são controles distintos. “Enabled” indica que a função está habilitada naquele escopo; não garante que exista vulnerabilidade, correção ou PR naquele momento.

Na configuração da organização, <code>Not set</code> significa que ela não impõe um estado para o recurso; o valor já definido no repositório continua valendo. Isso não desliga Security updates. Para desabilitar, é preciso conferir o estado efetivo nas configurações do repositório ou aplicar <code>Disabled</code> pela configuração da organização.

Rulesets e proteção de branch definem condições de merge, como checks obrigatórios. São separados de habilitar grafo, alertas e atualizações. Uma regra que exige um job sempre pulado não proporciona a revisão indicada pelo nome.

Um ruleset pode ser criado no nível da organização e direcionado a todos ou a repositórios selecionados, desde que o plano da organização permita rulesets organizacionais (GitHub Team ou Enterprise). Nele, é possível exigir um check como **Dependency Review**. No plano Free desta organização, essa opção organizacional não está disponível para aplicação; use a proteção de branch ou ruleset do próprio repositório público.

## Exemplo usado nos testes

Em outubro de 2026, um PR de teste adicionou <code>org.apache.commons:commons-compress</code> versão <code>1.25.0</code> com escopo Maven <code>test</code>. O GitHub Advisory Database associa a versão a duas vulnerabilidades moderadas; a versão corrigida indicada é <code>1.26.0</code>:

- [CVE-2024-25710 / GHSA-4g9r-vxhx-9pgx](https://github.com/advisories/GHSA-4g9r-vxhx-9pgx)
- [CVE-2024-26308 / GHSA-4265-ccf5-phj5](https://github.com/advisories/GHSA-4265-ccf5-phj5)

O PR de teste foi mesclado à <code>main</code> para permitir observar o comportamento do Dependabot. A dependência de teste agora faz parte do estado do repositório. O escopo <code>test</code> a mantém fora do runtime normal da aplicação, mas continua sendo dependência do projeto e pode aparecer no grafo e nos alertas. Ao terminar o exercício, remova-a ou atualize para uma versão corrigida e confira os alertas.

Na mesma validação, Dependency Review apareceu como <code>skipped</code> porque o job estava condicionalmente desativado. A leitura atual do ruleset mostrou que ele ainda espera esse nome como check obrigatório; isso não significa que o job tenha analisado o PR.

## Exemplo combinado de Code Scanning e Dependabot

No PR de demonstração aberto nesta branch, o CodeQL identificou um novo alerta de alta severidade de SQL injection no exemplo Java isolado em teste. O build do Maven passou. Isso confirma que o Code Scanning analisa o código alterado no PR, mesmo quando o exemplo não está conectado a uma rota da aplicação.

O mesmo PR adiciona `org.apache.commons:commons-configuration2` versão `2.14.0`, em escopo `test`, associada ao advisory moderado [GHSA-337m-mw94-2v6g](https://github.com/advisories/GHSA-337m-mw94-2v6g); a versão corrigida indicada é `2.15.0`. O check **Dependency Review** apareceu como `skipped`, pois o job está temporariamente condicionado para não executar. Portanto, ele não avaliou a mudança de dependência neste PR.

A distinção prática: **Dependabot alerts** registra vulnerabilidades encontradas no grafo do repositório; **Dependency Review** é o check que avalia a alteração de dependência dentro do PR. Com o workflow de Dependency Review pulado, não se deve esperar que esse check valide a dependência. Não mescle uma dependência vulnerável à branch principal apenas para testar sem decidir conscientemente: ao chegar à branch padrão, pode surgir um alerta do Dependabot e, dependendo da configuração efetiva no repositório, uma atualização automática.

## Estado observado durante esta compilação

Este retrato pode mudar e não substitui as configurações atuais:

- Na configuração de segurança da organização, Dependency graph e Dependabot alerts foram vistos como habilitados. Security updates foi depois informado como <code>Not set</code>; nesse estado, a organização não altera o valor que já está definido no repositório. Automatic dependency submission, restrição a dismiss direto e Malware alerts estavam como <code>Not set</code>.
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
