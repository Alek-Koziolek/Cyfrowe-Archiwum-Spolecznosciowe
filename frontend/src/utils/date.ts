export function isoToDisplay(
  value: string,
  precision: 'year' | 'month' | 'day' | '',
): string {
  if (!value) return '';
  if (precision === 'day') {
    const [y, m, d] = value.split('-');
    if (y && m && d) return `${d}.${m}.${y}`;
  } else if (precision === 'month') {
    const [y, m] = value.split('-');
    if (y && m) return `${m}.${y}`;
  }
  return value;
}

export function displayToIso(
  value: string,
  precision: 'year' | 'month' | 'day' | '',
): string {
  if (!value) return '';
  if (precision === 'day') {
    const [d, m, y] = value.split('.');
    if (d && m && y) return `${y}-${m}-${d}`;
  } else if (precision === 'month') {
    const [m, y] = value.split('.');
    if (m && y) return `${y}-${m}`;
  }
  return value;
}

export function maskDateInput(
  raw: string,
  precision: 'year' | 'month' | 'day' | '',
): string {
  const digits = raw.replace(/\D/g, '');
  if (precision === 'day') {
    let out = digits.slice(0, 2);
    if (digits.length > 2) out += '.' + digits.slice(2, 4);
    if (digits.length > 4) out += '.' + digits.slice(4, 8);
    return out;
  } else if (precision === 'month') {
    let out = digits.slice(0, 2);
    if (digits.length > 2) out += '.' + digits.slice(2, 6);
    return out;
  }
  return digits.slice(0, 4);
}

export function formatDate(
  dateTaken: string | null,
  precision: 'year' | 'month' | 'day' | null,
): string {
  if (!dateTaken) return '';

  const parts = dateTaken.split('-');
  const year = parts[0];
  const month = parts[1];

  switch (precision) {
    case 'year':
      return year;
    case 'month': {
      if (!month) return year;
      const date = new Date(Number(year), Number(month) - 1);
      return date.toLocaleDateString('pl-PL', {
        year: 'numeric',
        month: 'long',
      });
    }
    case 'day':
    default: {
      const [y, m, d] = dateTaken.split('-');
      if (y && m && d) return `${d}.${m}.${y}`;
      return dateTaken;
    }
  }
}
