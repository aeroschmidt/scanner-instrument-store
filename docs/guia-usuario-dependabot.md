# Dependabot: guia rápido para quem contribui

O Dependabot acompanha as dependências reconhecidas pelo GitHub e ajuda a identificar versões com vulnerabilidades conhecidas. Um alerta indica que uma dependência está em uma faixa afetada; ele deve ser investigado, mas, sozinho, não confirma que a aplicação foi explorada.

## Onde encontrar um alerta

No repositório, abra **Security** (em algumas interfaces, **Security and quality**) e selecione **Dependabot** ou **Dependabot alerts**. Abra o alerta para consultar:

- pacote e arquivo de dependências envolvidos;
- severidade e versões afetadas;
- versão corrigida, quando disponível;
- caminho da dependência — direta ou trazida por outra dependência;
- Pull Request de correção, se o Dependabot já tiver criado um.

Se a opção não aparecer ou você não puder abrir o alerta, peça à pessoa mantenedora para confirmar a configuração e seu acesso. A ausência de alertas não prova que todas as dependências estão livres de problemas: o GitHub depende dos arquivos de dependência reconhecidos e dos avisos disponíveis na base de advisories.

## O que o Dependabot pode fazer

| Recurso | Para que serve |
|---|---|
| **Dependabot alerts** | Avisa quando uma dependência usada corresponde a uma vulnerabilidade conhecida. |
| **Dependabot security updates** | Pode abrir um PR para atualizar uma dependência vulnerável quando existe uma versão corrigida compatível e o recurso está habilitado. |
| **Dependabot version updates** | Pode abrir PRs periódicos para manter dependências atualizadas, mesmo sem alerta de vulnerabilidade. A mantenedora define a configuração e a agenda. |

Esses recursos são separados. O Dependabot pode propor uma atualização, mas o PR ainda precisa ser analisado, passar pelas verificações do projeto e seguir o processo de revisão e merge da equipe.

![Captura histórica do painel Advanced Security mostrando os controles separados de Dependabot alerts, security updates e version updates](capturas/04-dependabot-codeql-config.jpg)

*Esta captura arquivada ilustra a separação entre os recursos. Os controles aparecem desligados no momento registrado pela imagem; ela não informa o estado atual de um repositório.*

## Como agir

1. Abra os detalhes do alerta e confira pacote, severidade, versões afetadas e arquivo indicado.
2. Verifique se há uma versão corrigida e se a dependência está declarada diretamente ou vem por meio de outra biblioteca.
3. Se houver um PR do Dependabot, revise os arquivos alterados e a versão proposta. Confira as verificações de compilação e testes do GitHub Actions; avalie compatibilidade antes da aprovação.
4. Se não houver PR, se os testes falharem ou se o impacto não estiver claro, peça orientação à pessoa mantenedora. Conforme o processo da equipe, ela pode preparar uma atualização manual ou investigar a dependência.
5. Prefira corrigir a dependência. Use **Dismiss** somente após analisar o alerta e confirmar, com a mantenedora, que não é necessária uma correção; registre o motivo de acordo com o processo do repositório.

Pessoas contribuidoras normalmente não administram as configurações organizacionais do Dependabot. Elas podem consultar os alertas e colaborar na correção; a mantenedora controla quais recursos estão habilitados e como as atualizações automáticas são propostas.

## Documentação oficial

- [Dependabot quickstart](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/dependabot-quickstart)
- [Visualizar e atualizar Dependabot alerts](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-dependabot-alerts/view-dependabot-alerts)
- [Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates)
- [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates)
