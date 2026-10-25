<script setup lang='ts'>
    const currencyFormatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    });

    export function formatCurrency(value: number): string {
        return currencyFormatter.format(value);
    }

    export function formatDate(isoDate: string | null): string {
        if (!isoDate) return '-';
        // Evita o deslocamento de fuso ao interpretar "YYYY-MM-DD" como UTC
        const [year, month, day] = isoDate.split('-');
        return `${day}/${month}/${year}`;
    }
</script>