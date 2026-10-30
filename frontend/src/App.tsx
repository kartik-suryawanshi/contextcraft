import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardScreen } from './features/dashboard/DashboardScreen';
import { WorkflowScreen } from './features/workflow/WorkflowScreen';
import { MemoryExplorerScreen } from './features/memory/MemoryExplorerScreen';
import { ExecutionPlaygroundScreen } from './features/executions/ExecutionPlaygroundScreen';
import { MemoryInspectorScreen } from './features/memory-inspector/MemoryInspectorScreen';
import { api } from './services/api';
import type { HealthStatus } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [selectedExecutionId, setSelectedExecutionId] = useState<string | null>(null);

  useEffect(() => {
    api.getHealth()
      .then((h) => setHealth(h))
      .catch((err) => {
        console.warn('Backend connection notice', err);
        setHealth({
          status: 'connecting',
          service: 'ContextCraft',
          database: 'unknown',
          mock_mode: true,
        });
      });
  }, []);

  const handleInspectExecutionInWorkflow = (executionId: string) => {
    setSelectedExecutionId(executionId);
    setActiveTab('workflow');
  };

  const handleInspectExecutionInMemoryViews = (executionId: string) => {
    setSelectedExecutionId(executionId);
    setActiveTab('inspector');
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] text-[#20242C] flex flex-col font-sans selection:bg-[#EEF0FD] selection:text-[#5558D9]">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        {activeTab === 'dashboard' && (
          <DashboardScreen onNavigateToExecution={handleInspectExecutionInWorkflow} />
        )}
        {activeTab === 'workflow' && (
          <WorkflowScreen selectedExecutionId={selectedExecutionId} />
        )}
        {activeTab === 'memory' && <MemoryExplorerScreen />}
        {activeTab === 'executions' && (
          <ExecutionPlaygroundScreen
            onInspectWorkflow={handleInspectExecutionInWorkflow}
            onInspectMemoryViews={handleInspectExecutionInMemoryViews}
          />
        )}
        {activeTab === 'inspector' && (
          <MemoryInspectorScreen selectedExecutionId={selectedExecutionId} />
        )}
      </main>

      <footer className="border-t border-[#E6E8EC] bg-white py-3 px-4 text-center text-xs text-[#98A2B3]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>ContextCraft &mdash; Memory-Orchestration Middleware for LangGraph</span>
          <span className="font-mono text-[11px] text-[#98A2B3]">
            Decoupled Control State · Conflict Detection · Token Budget Enforcement
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
