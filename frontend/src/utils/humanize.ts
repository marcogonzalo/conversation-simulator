/**
 * Utility functions for humanizing slugs and IDs
 */

/**
 * Converts a snake_case or kebab-case string to a human-readable format
 * @param slug - The string to humanize (e.g., "ana_garcia", "negociacion_erp")
 * @returns Human-readable string (e.g., "Ana Garcia", "Negociacion Erp")
 */
export const humanize = (slug: string): string => {
  return slug
    .split(/[_-]/) // Split on underscore or dash
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Humanizes a persona ID for display
 * @param personaId - The persona ID (e.g., "ana_garcia")
 * @returns Human-readable persona name (e.g., "Ana Garcia")
 */
export const humanizePersona = (personaId: string): string => {
  return humanize(personaId);
};

/**
 * Humanizes a context ID for display
 * @param contextId - The context ID (e.g., "negociacion_erp")
 * @returns Human-readable context name (e.g., "Negociacion Erp")
 */
export const humanizeContext = (contextId: string): string => {
  return humanize(contextId);
};
