# Som & Corda — loja de instrumentos

Aplicação de demonstração em Java 21 e Maven para aprender o ciclo de desenvolvimento, testes e análise de segurança. Tem uma página web para consultar/manter itens, API REST, banco H2 em memória e testes de integração.

Pasta local: `C:\Applications\git\loja-instrumentos`.

## Abrir no Eclipse

1. No Eclipse, escolha **File > Import > Maven > Existing Maven Projects**.
2. Selecione esta pasta (a que contém `pom.xml`) e finalize a importação.
3. Aguarde o Maven baixar as dependências. Configure um JDK 21 em **Window > Preferences > Java > Installed JREs** se o Eclipse ainda não tiver um.
4. Execute `LojaInstrumentosApplication` como **Java Application**.
5. Abra `http://localhost:8080`.

Também há metadados `.project` e `.classpath` para IDEs Eclipse que usem m2e; a importação Maven é a forma recomendada.

## Executar com Maven

É necessário JDK 21. O Maven Wrapper baixa e usa Maven 3.10.0 sem exigir que o Maven esteja instalado no PATH. Em um terminal nesta pasta:

```powershell
.\mvnw.cmd clean verify
.\mvnw.cmd spring-boot:run
```

O primeiro comando compila o código e executa os testes. O segundo inicia a aplicação; acesse `http://localhost:8080`. Os dados de exemplo voltam ao estado inicial quando a aplicação reinicia porque o H2 é em memória.

## GitHub Actions e segurança do repositório

### Como está funcionando

O workflow `.github/workflows/build.yml` executa Maven `verify` em pushes para `main` e em pull requests destinados a `main`. O CodeQL está no **Default setup**, gerenciado pelas configurações do GitHub. O arquivo `.github/workflows/codeql.yml` não controla a análise enquanto esse modo estiver ativo; o GitHub o desabilitou manualmente ao ativar o Default setup.

O GitHub Actions reage aos eventos e organiza a execução; o Maven compila e roda os testes. CodeQL analisa o código e publica os achados em **Security > Code scanning** e nos checks do pull request. A frequência da análise CodeQL é controlada pelo Default setup, não pelo cron do arquivo YAML.

A exportação de métricas proposta no PR #12 usa um workflow separado, `.github/workflows/code-scanning-metrics.yml`, para consultar a API do GitHub e publicar um artifact por execução com snapshots JSON/CSV. Depois que o PR for aprovado e mesclado, o workflow rodará em push na `main`, diariamente ao meio-dia de Brasília e manualmente. Para um snapshot de PR específico, a mantenedora pode executar o workflow manualmente na `main` e informar o número do PR; o workflow lê seus resultados pela API e não executa seu código. A execução manual é permitida apenas na branch padrão. O agendamento diário cria uma fotografia das métricas; não força uma nova análise CodeQL. O `GITHUB_TOKEN` recebe apenas leitura de Code Scanning, pull requests e contents, sem Personal Access Token. Os artifacts expiram em até 90 dias; snapshots contam alertas atualmente dispensados e não formam um log permanente de cada evento de dismiss.

### Estado dos recursos de segurança

CodeQL/Code Scanning está em **Default setup**, gerenciado pela interface do GitHub. Dependabot e Secret Protection permanecem desligados até serem testados em etapas separadas. Em repositórios públicos, a detecção de padrões de segredos para alertar provedores parceiros pode ocorrer automaticamente mesmo quando o Secret Protection e os alertas para o proprietário estão desligados; consulte a documentação oficial antes de interpretar isso como ausência absoluta de detecção.

Copilot Autofix aparece ligado nas configurações, mas depende de alertas do CodeQL para sugerir correções e não substitui uma análise ativa. Não o alteramos nesta etapa.

O estado observado e os procedimentos separados para administração e PRs estão nos guias da [mantenedora em Word](docs/guia-github-actions-e-seguranca.docx) e [Markdown](docs/guia-github-actions-e-seguranca.md), e de [autoria de PRs em Word](docs/guia-usuario-prs.docx) e [Markdown](docs/guia-usuario-prs.md). As capturas estão em `docs/capturas/`.

### Ordem acordada para os testes

> **Lembrete:** testar e documentar uma ferramenta do GitHub por vez, para entender o que cada check faz.

Sequência de estudo:

1. Entender os eventos (`push`, `pull_request` e `schedule`), jobs, etapas, logs e checks no GitHub Actions.
2. Observar o CodeQL gerenciado e os relatórios diários de métricas em **Actions** e os achados em **Security > Code scanning**.
3. Em etapas futuras, testar Dependabot e Secret Scanning separadamente e registrar cada resultado.

Este README e os guias documentam o estado e os procedimentos observados. O CircleCI não faz parte do workflow atual.

## API

- `GET /api/products` — lista itens
- `GET /api/products/{id}` — consulta um item
- `POST /api/products` — cadastra item
- `PUT /api/products/{id}` — atualiza item
- `DELETE /api/products/{id}` — remove item

Exemplo de corpo JSON: `{"name":"Violão","category":"Cordas","price":799.90,"stock":8}`.
