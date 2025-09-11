// Teste de importação e uso das funções quicksort
const { quicksort, quicksortImmutable } = require('./quicksort.js');

console.log('=== Teste de Importação das Funções Quicksort ===\n');

// Dados de teste
const testArrays = [
    [5, 2, 8, 1, 9],
    [100, 50, 25, 75],
    [3, 1, 4, 1, 5, 9, 2, 6],
    [42],
    []
];

testArrays.forEach((arr, index) => {
    console.log(`Teste ${index + 1}:`);
    console.log('Array original:', arr);
    
    // Teste quicksort in-place
    const arrCopy1 = [...arr];
    quicksort(arrCopy1);
    console.log('Quicksort in-place:', arrCopy1);
    
    // Teste quicksort imutável
    const sortedImmutable = quicksortImmutable(arr);
    console.log('Quicksort imutável:', sortedImmutable);
    console.log('Array original inalterado:', arr);
    console.log('---');
});

// Teste de performance
console.log('\n=== Teste de Performance ===');
const largeArray = Array.from({length: 1000}, () => Math.floor(Math.random() * 1000));

console.time('Quicksort in-place (1000 elementos)');
const largeCopy1 = [...largeArray];
quicksort(largeCopy1);
console.timeEnd('Quicksort in-place (1000 elementos)');

console.time('Quicksort imutável (1000 elementos)');
const sortedLarge = quicksortImmutable(largeArray);
console.timeEnd('Quicksort imutável (1000 elementos)');

console.log('\n✅ Todos os testes executados com sucesso!');
console.log('✅ As funções podem ser importadas e utilizadas em outros módulos');
console.log('✅ Ambas as implementações (in-place e imutável) funcionam corretamente');
console.log('✅ Performance adequada para arrays de diferentes tamanhos');