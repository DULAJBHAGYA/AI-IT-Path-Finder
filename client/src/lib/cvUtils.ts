import { CVData } from '@/types/cv';

export function generateJSON(data: CVData): string {
  return JSON.stringify(data, null, 2);
}

export function downloadJSON(data: CVData): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'cv-data.json';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
