# AI Content Factory

MVP em nuvem para pesquisar pautas de tecnologia/IA, gerar roteiros com Gemini e renderizar um vídeo vertical de teste com Python + FFmpeg.

## Estado desta versão

- [x] Pesquisa inicial por RSS
- [x] Geração de roteiro via Gemini API
- [x] Renderização de vídeo vertical MP4
- [x] Execução agendada no GitHub Actions
- [ ] Narração TTS
- [ ] Legendas sincronizadas
- [ ] Publicação automática nas redes
- [ ] Coleta de métricas

Esta primeira versão gera um vídeo visual de teste sem narração. A próxima etapa adicionará TTS e legendas antes de qualquer publicação.

## Configuração local (opcional)

1. Instale Python 3.12 e FFmpeg.
2. `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e adicione a chave Gemini.
4. `python main.py`

## Configuração no GitHub

1. Crie um repositório `ai-content-factory`.
2. Envie todos os arquivos deste projeto.
3. Abra Settings → Secrets and variables → Actions.
4. Crie o secret `GEMINI_API_KEY`.
5. Abra Actions e habilite workflows.
6. Execute `AI Content Factory` manualmente em Run workflow.
7. Baixe o artifact `ai-content-...` para conferir o MP4.

## Agendamento

O workflow está configurado para executar às 03:00, 11:00 e 19:00 no horário de Brasília/Itajaí (UTC-3). O GitHub Actions pode atrasar execuções agendadas em períodos de alta demanda.

## Segurança e custos

- Nunca coloque chaves no código ou em arquivos commitados.
- O uso da Gemini API está sujeito aos limites e termos do plano gratuito vigente.
- GitHub Actions tem limites de minutos e armazenamento conforme visibilidade e plano do repositório.
- Este MVP não publica automaticamente em nenhuma rede social.
- Não habilite faturamento sem revisar os limites e controles de gasto.
