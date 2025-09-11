/**
 * Implementação do algoritmo Quicksort em JavaScript
 * Complexidade: O(n log n) no caso médio, O(n²) no pior caso
 * @param {number[]} arr - Array de números para ordenar
 * @param {number} low - Índice inicial (padrão: 0)
 * @param {number} high - Índice final (padrão: arr.length - 1)
 * @returns {number[]} Array ordenado
 */
function quicksort(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        // Encontra o índice de partição
        const pivotIndex = partition(arr, low, high);
        
        // Recursivamente ordena os elementos antes e depois da partição
        quicksort(arr, low, pivotIndex - 1);
        quicksort(arr, pivotIndex + 1, high);
    }
    return arr;
}

/**
 * Função de partição que coloca o pivot na posição correta
 * @param {number[]} arr - Array a ser particionado
 * @param {number} low - Índice inicial
 * @param {number} high - Índice final
 * @returns {number} Índice do pivot após partição
 */
function partition(arr, low, high) {
    // Escolhe o último elemento como pivot
    const pivot = arr[high];
    let i = low - 1; // Índice do menor elemento
    
    for (let j = low; j < high; j++) {
        // Se o elemento atual é menor ou igual ao pivot
        if (arr[j] <= pivot) {
            i++;
            [arr[i], arr[j]] = [arr[j], arr[i]]; // Troca elementos
        }
    }
    
    // Coloca o pivot na posição correta
    [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
    return i + 1;
}

/**
 * Versão simplificada que cria uma nova array (não modifica a original)
 * @param {number[]} arr - Array original
 * @returns {number[]} Nova array ordenada
 */
function quicksortImmutable(arr) {
    if (arr.length <= 1) return arr;
    
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    
    return [...quicksortImmutable(left), ...middle, ...quicksortImmutable(right)];
}

// Exemplos de uso:
const numbers = [64, 34, 25, 12, 22, 11, 90];
console.log('Array original:', numbers);

// Versão in-place (modifica a array original)
const sortedInPlace = [...numbers]; // Cópia para não modificar o original
quicksort(sortedInPlace);
console.log('Quicksort in-place:', sortedInPlace);

// Versão imutável (retorna nova array)
const sortedImmutable = quicksortImmutable(numbers);
console.log('Quicksort imutável:', sortedImmutable);

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { quicksort, quicksortImmutable, partition };
}

// Teste de performance
function performanceTest() {
    const largeArray = Array.from({length: 10000}, () => Math.floor(Math.random() * 10000));
    
    console.time('Quicksort Performance');
    const sorted = quicksortImmutable([...largeArray]);
    console.timeEnd('Quicksort Performance');
    
    console.log('Array de 10.000 elementos ordenado com sucesso!');
    console.log('Primeiros 10 elementos:', sorted.slice(0, 10));
    console.log('Últimos 10 elementos:', sorted.slice(-10));
}

// Descomente a linha abaixo para executar o teste de performance
// performanceTest();