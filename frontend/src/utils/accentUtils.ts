/**
 * Utility functions for accent handling
 */

/**
 * Humanizes accent values for display
 */
export function humanizeAccent(accent: string): string {
  const accentMap: Record<string, string> = {
    'caribbean_spanish': 'Caribeño (Cubano)',
    'peruvian_spanish': 'Peruano',
    'venezuelan_spanish': 'Venezolano',
    'florida_english': 'Inglés (Florida)',
    'mexican_spanish': 'Mexicano',
    'colombian_spanish': 'Colombiano',
    'argentinian_spanish': 'Argentino',
    'chilean_spanish': 'Chileno',
    'spain_spanish': 'Español (España)',
    'neutral': 'Neutral'
  }
  
  return accentMap[accent] || accent
}

/**
 * Gets accent color for UI display
 */
export function getAccentColor(accent: string): string {
  const colorMap: Record<string, string> = {
    'caribbean_spanish': 'text-orange-600',
    'peruvian_spanish': 'text-red-600',
    'venezuelan_spanish': 'text-yellow-600',
    'florida_english': 'text-blue-600',
    'mexican_spanish': 'text-green-600',
    'colombian_spanish': 'text-yellow-500',
    'argentinian_spanish': 'text-sky-600',
    'chilean_spanish': 'text-red-500',
    'spain_spanish': 'text-purple-600',
    'neutral': 'text-gray-600'
  }
  
  return colorMap[accent] || 'text-gray-600'
}
