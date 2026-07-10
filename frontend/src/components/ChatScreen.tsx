import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import * as api from "../lib/api";
import type { Appointment, AppointmentDetail, DashboardSummary, Turn, YardAlert } from "../lib/types";
import MessageBubble from "./MessageBubble";
import Composer from "./Composer";

function updateLastAssistant(turns: Turn[], content: string): Turn[] {
  const copy = [...turns];
  for (let i = copy.length - 1; i >= 0; i--) {
    const turn = copy[i];
    if (turn.role === "assistant") {
      copy[i] = { ...turn, content: turn.content + content };
      break;
    }
  }
  return copy;
}

function finishLastAssistant(turns: Turn[], error?: string): Turn[] {
  const copy = [...turns];
  for (let i = copy.length - 1; i >= 0; i--) {
    const turn = copy[i];
    if (turn.role === "assistant") {
      copy[i] = { ...turn, streaming: false, error };
      break;
    }
  }
  return copy;
}

function formatDate(value?: string | null): string {
  if (!value) return "-";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

const statusLabel: Record<string, string> = {
  pending: "Pendente",
  checked_in: "Check-in",
  receiving: "Recebendo",
  completed: "Realizado",
  cancelled: "Cancelado",
  no_show: "No-show",
};

export default function ChatScreen() {
  const { email, sessionToken, logout } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [alerts, setAlerts] = useState<YardAlert[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<AppointmentDetail | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);

  const openAlerts = useMemo(() => alerts.filter((alert) => alert.status === "open"), [alerts]);

  async function refreshOperationalData(nextSelectedId?: number | null) {
    if (!sessionToken) return;
    setLoading(true);
    setError(null);
    try {
      const [nextSummary, nextAppointments, nextAlerts] = await Promise.all([
        api.agendaiSummary(sessionToken),
        api.listAgendaiAppointments(sessionToken),
        api.listAgendaiAlerts(sessionToken),
      ]);
      setSummary(nextSummary);
      setAppointments(nextAppointments);
      setAlerts(nextAlerts);
      const firstId = nextAppointments[0]?.id ?? null;
      setSelectedId(nextSelectedId ?? selectedId ?? firstId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar operação.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setTurns([]);
    setSelectedId(null);
    setDetail(null);
    void refreshOperationalData(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionToken]);

  useEffect(() => {
    if (!sessionToken || selectedId === null) {
      setDetail(null);
      return;
    }
    api
      .getAgendaiAppointment(sessionToken, selectedId)
      .then(setDetail)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro ao carregar detalhe."));
  }, [sessionToken, selectedId]);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [turns]);

  async function handleGenerateAlerts() {
    if (!sessionToken) return;
    setLoading(true);
    setError(null);
    try {
      await api.generateAgendaiLateAlerts(sessionToken);
      await refreshOperationalData(selectedId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar alertas.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSend(text: string) {
    if (!sessionToken || sending) return;
    setTurns((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", steps: [], content: "", streaming: true },
    ]);
    setSending(true);
    try {
      for await (const chunk of api.streamChat(sessionToken, [{ role: "user", content: text }])) {
        setTurns((prev) => updateLastAssistant(prev, chunk));
      }
      setTurns((prev) => finishLastAssistant(prev));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao conversar com o agente.";
      setTurns((prev) => finishLastAssistant(prev, message));
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-full flex-col bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-semibold text-zinc-950">AgendAI</h1>
            <p className="text-xs text-zinc-500">{email}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => refreshOperationalData(selectedId)}
              disabled={loading}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm hover:bg-zinc-100 disabled:opacity-50"
            >
              Atualizar
            </button>
            <button
              onClick={handleGenerateAlerts}
              disabled={loading}
              className="rounded-lg bg-amber-600 px-3 py-2 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
            >
              Gerar alertas
            </button>
            <button
              onClick={logout}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm hover:bg-zinc-100"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
        <section className="flex min-h-0 flex-col gap-4">
          {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

          <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
            <SummaryTile label="Pendentes" value={summary?.pending_appointments ?? 0} />
            <SummaryTile label="Realizados" value={summary?.completed_appointments ?? 0} />
            <SummaryTile label="Check-ins" value={summary?.check_ins ?? 0} />
            <SummaryTile label="Atrasadas" value={summary?.late_loads ?? 0} tone="alert" />
          </div>

          <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 xl:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.1fr)]">
            <section className="min-h-0 overflow-hidden rounded-lg border border-zinc-200 bg-white">
              <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3">
                <h2 className="text-sm font-semibold text-zinc-900">Agendamentos</h2>
                <span className="text-xs text-zinc-500">{appointments.length}</span>
              </div>
              <div className="max-h-full overflow-y-auto">
                {appointments.length === 0 ? (
                  <EmptyState label="Nenhum agendamento encontrado" />
                ) : (
                  appointments.map((appointment) => (
                    <button
                      key={appointment.id}
                      onClick={() => setSelectedId(appointment.id)}
                      className={`block w-full border-b border-zinc-100 px-4 py-3 text-left hover:bg-zinc-50 ${
                        selectedId === appointment.id ? "bg-emerald-50" : "bg-white"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate text-sm font-medium text-zinc-950">
                          #{appointment.id} {appointment.load_reference ?? "Sem referência"}
                        </span>
                        <StatusBadge status={appointment.status} />
                      </div>
                      <div className="mt-1 text-xs text-zinc-500">{formatDate(appointment.scheduled_at)}</div>
                      <div className="mt-1 text-xs text-zinc-500">{appointment.dock ?? "Doca não definida"}</div>
                    </button>
                  ))
                )}
              </div>
            </section>

            <section className="min-h-0 overflow-y-auto rounded-lg border border-zinc-200 bg-white">
              <div className="border-b border-zinc-200 px-4 py-3">
                <h2 className="text-sm font-semibold text-zinc-900">Detalhe do recebimento</h2>
              </div>
              {detail ? <AppointmentDetailPanel detail={detail} /> : <EmptyState label="Selecione um agendamento" />}
            </section>
          </div>
        </section>

        <aside className="grid min-h-0 grid-rows-[auto_minmax(0,1fr)] gap-4">
          <section className="rounded-lg border border-zinc-200 bg-white">
            <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-zinc-900">Alertas abertos</h2>
              <span className="text-xs text-zinc-500">{openAlerts.length}</span>
            </div>
            <div className="max-h-48 overflow-y-auto">
              {openAlerts.length === 0 ? (
                <EmptyState label="Nenhum alerta aberto" compact />
              ) : (
                openAlerts.map((alert) => (
                  <div key={alert.id} className="border-b border-zinc-100 px-4 py-3">
                    <div className="text-sm font-medium text-zinc-900">Agendamento #{alert.appointment_id}</div>
                    <p className="mt-1 text-sm text-zinc-600">{alert.message}</p>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-zinc-200 bg-white">
            <div className="border-b border-zinc-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-zinc-900">Agente</h2>
            </div>
            <div ref={chatRef} className="min-h-0 flex-1 overflow-y-auto p-4">
              {turns.length === 0 ? (
                <EmptyState label="Faça uma pergunta ao AgendAI" />
              ) : (
                <div className="space-y-3">
                  {turns.map((turn, index) =>
                    turn.role === "user" ? (
                      <MessageBubble key={index} message={{ role: "user", content: turn.content }} />
                    ) : (
                      <div key={index}>
                        <MessageBubble
                          message={{ role: "assistant", content: turn.content }}
                          pending={turn.streaming && !turn.content}
                        />
                        {turn.error && <div className="mt-2 text-sm text-red-600">{turn.error}</div>}
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>
            <Composer onSend={handleSend} disabled={sending} />
          </section>
        </aside>
      </main>
    </div>
  );
}

function SummaryTile({ label, value, tone }: { label: string; value: number; tone?: "alert" }) {
  const color = tone === "alert" ? "text-amber-700" : "text-emerald-700";
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-4 py-3">
      <div className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${color}`}>{value}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className="shrink-0 rounded-full bg-zinc-100 px-2 py-1 text-xs font-medium text-zinc-700">
      {statusLabel[status] ?? status}
    </span>
  );
}

function EmptyState({ label, compact }: { label: string; compact?: boolean }) {
  return <div className={`px-4 text-center text-sm text-zinc-500 ${compact ? "py-6" : "py-12"}`}>{label}</div>;
}

function AppointmentDetailPanel({ detail }: { detail: AppointmentDetail }) {
  return (
    <div className="space-y-5 p-4">
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-base font-semibold text-zinc-950">Agendamento #{detail.appointment.id}</h3>
          <StatusBadge status={detail.appointment.status} />
        </div>
        <dl className="mt-3 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <Info label="Horário" value={formatDate(detail.appointment.scheduled_at)} />
          <Info label="Doca" value={detail.appointment.dock ?? "-"} />
          <Info label="Referência" value={detail.appointment.load_reference ?? "-"} />
          <Info label="Criado em" value={formatDate(detail.appointment.created_at)} />
        </dl>
      </div>

      <div>
        <h4 className="text-sm font-semibold text-zinc-900">Motorista e veículo</h4>
        <dl className="mt-3 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <Info label="Motorista" value={detail.driver.name} />
          <Info label="Empresa" value={detail.driver.company ?? "-"} />
          <Info label="Placa" value={detail.vehicle.plate} />
          <Info label="Modelo" value={detail.vehicle.model ?? "-"} />
        </dl>
      </div>

      <div>
        <h4 className="text-sm font-semibold text-zinc-900">Fornecedor</h4>
        <dl className="mt-3 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <Info label="Nome" value={detail.supplier.name} />
          <Info label="E-mail" value={detail.supplier.contact_email ?? "-"} />
        </dl>
      </div>

      <div>
        <h4 className="text-sm font-semibold text-zinc-900">Check-ins</h4>
        {detail.check_ins.length === 0 ? (
          <p className="mt-2 text-sm text-zinc-500">Nenhum check-in registrado.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {detail.check_ins.map((checkIn) => (
              <div key={checkIn.id} className="rounded-lg border border-zinc-200 px-3 py-2 text-sm">
                {formatDate(checkIn.checked_in_at)} · {checkIn.method}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</dt>
      <dd className="mt-1 break-words text-zinc-900">{value}</dd>
    </div>
  );
}
