/**
 * Shared React components
 */

// Export types only - implementations are in case studies
export interface SPARQLSectionProps {
  orchestratorUrl: string;
  defaultQuery?: string;
}

export interface EntityCardProps {
  entityId: string;
  label: string;
  type: string;
  onClick?: () => void;
}

export interface HealthStatusProps {
  orchestratorUrl: string;
}
