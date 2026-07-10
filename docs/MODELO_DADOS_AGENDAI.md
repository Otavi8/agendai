# Modelo de Dados Inicial do AgendAI

Este modelo cobre o MVP confirmado no `CONTEXT.md`: PostgreSQL Docker como fonte principal e integrações externas em stub.

## Tabelas

### `agendai_driver`

Cadastro do motorista.

- `id`: identificador interno.
- `name`: nome do motorista.
- `cpf`: CPF do motorista. Dado sensível.
- `email`: e-mail usado para confirmação/cadastro. Dado sensível.
- `phone`: telefone/WhatsApp. Dado sensível.
- `company`: transportadora ou empresa relacionada.
- `notes`: observações operacionais.

### `agendai_vehicle`

Veículo associado ao motorista.

- `id`: identificador interno.
- `driver_id`: motorista proprietário/condutor.
- `plate`: placa. Dado sensível operacional.
- `model`: modelo do veículo.
- `color`: cor do veículo.
- `year`: ano do veículo.

### `agendai_supplier`

Fornecedor ou origem da carga.

- `id`: identificador interno.
- `name`: nome do fornecedor.
- `contact_email`: e-mail para confirmação de agendamento.
- `contact_phone`: telefone de contato.
- `authorized_email_domain`: domínio autorizado para envio futuro de confirmações.

### `agendai_appointment`

Agendamento de recebimento.

- `id`: identificador interno.
- `driver_id`: motorista agendado.
- `vehicle_id`: veículo agendado.
- `supplier_id`: fornecedor.
- `scheduled_at`: horário previsto.
- `dock`: doca/local de recebimento.
- `load_reference`: referência da carga, NF, pedido ou documento.
- `status`: `pending`, `checked_in`, `receiving`, `completed`, `cancelled`, `no_show`.
- `notes`: observações.
- `created_by_user_id`: usuário interno que criou o agendamento.

### `agendai_check_in`

Registro de chegada/check-in.

- `id`: identificador interno.
- `appointment_id`: agendamento relacionado.
- `checked_in_at`: horário do check-in.
- `method`: origem do check-in, como `qr_code` ou `manual`.
- `confirmed_by_user_id`: usuário interno que confirmou quando aplicável.
- `notes`: observações.

### `agendai_yard_alert`

Alertas operacionais de pátio.

- `id`: identificador interno.
- `appointment_id`: agendamento relacionado.
- `alert_type`: tipo, como `late_check_in`.
- `severity`: `info`, `warning`, `critical`.
- `message`: mensagem para a equipe de recebimento.
- `status`: `open`, `acknowledged`, `resolved`.
- `created_at`: data de criação herdada do modelo base.
- `resolved_at`: data de resolução.
- `resolved_by_user_id`: usuário que resolveu.

### `agendai_business_rule_document`

Metadados de documentos de regras de negócio.

- `id`: identificador interno.
- `file_name`: nome do arquivo.
- `source`: origem lógica, inicialmente `stub`.
- `bucket`: bucket futuro no MinIO.
- `object_key`: chave futura do objeto no MinIO.
- `status`: `stub`, `uploaded`, `indexed`, `disabled`.

## Dados Sensíveis

- CPF, e-mail, telefone, placa, referência da carga e histórico de recebimentos.
- O agente não deve expor esses dados para motoristas ou fornecedores.
- Alterações em agendamentos, motoristas e veículos devem exigir confirmação humana.

## Regras de Acesso no MVP

- O MVP reutiliza a autenticação JWT existente.
- Controle fino por grupos será implementado depois; por enquanto, as rotas do domínio exigem sessão autenticada.
- Futuramente os grupos esperados são: `analytics_admin`, `recebimento_operador` e `consulta_restrita`.

