#!/usr/bin/env node

/**
 * Script para identificar e remover código obsoleto
 * Executa análise de componentes e sugere limpezas
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração
const PROJECT_ROOT = path.join(__dirname, '..');
const COMPONENTS_DIR = path.join(PROJECT_ROOT, 'components');
const CSS_FILE = path.join(PROJECT_ROOT, 'index.css');

// Padrões de código obsoleto
const OBSOLETE_PATTERNS = {
  // Classes CSS não utilizadas
  unusedCSS: /\.figma-[a-zA-Z-]+/g,

  // Classes hardcoded que deveriam usar tokens
  hardcodedSpacing: /(?:p-|m-|px-|py-|mx-|my-|gap-|space-y-|space-x-)\d+/g,

  // Componentes duplicados
  duplicateComponents: ['TicketList.tsx', 'NewTicketsList.tsx'],

  // Imports não utilizados
  unusedImports: /import.*from.*['"]\.\.\/.*['"];?\s*$/gm,
};

// Função para analisar arquivo
function analyzeFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const issues = [];

  // Verificar classes CSS não utilizadas
  const cssClasses = content.match(/className="([^"]*)"/g) || [];
  const usedClasses = new Set();

  cssClasses.forEach(match => {
    const classes = match.match(/className="([^"]*)"/)[1];
    classes.split(' ').forEach(cls => {
      if (cls.trim()) usedClasses.add(cls.trim());
    });
  });

  // Verificar espaçamentos hardcoded
  const hardcodedSpacing = content.match(OBSOLETE_PATTERNS.hardcodedSpacing) || [];
  if (hardcodedSpacing.length > 0) {
    issues.push({
      type: 'hardcoded-spacing',
      message: `Espaçamentos hardcoded encontrados: ${hardcodedSpacing.join(', ')}`,
      suggestions: ['Use tokens do design system', 'Considere usar createCardClasses() ou similar'],
    });
  }

  // Verificar imports não utilizados
  const imports = content.match(/import.*from.*['"]\.\.\/.*['"];?\s*$/gm) || [];
  imports.forEach(importLine => {
    const importPath = importLine.match(/from\s+['"]([^'"]+)['"]/);
    if (importPath) {
      const fullPath = path.resolve(path.dirname(filePath), importPath[1]);
      if (!fs.existsSync(fullPath + '.tsx') && !fs.existsSync(fullPath + '.ts')) {
        issues.push({
          type: 'unused-import',
          message: `Import não encontrado: ${importLine.trim()}`,
          suggestions: ['Remover import não utilizado', 'Verificar caminho do import'],
        });
      }
    }
  });

  return issues;
}

// Função para analisar CSS
function analyzeCSS() {
  const content = fs.readFileSync(CSS_FILE, 'utf8');
  const issues = [];

  // Encontrar classes figma não utilizadas
  const figmaClasses = content.match(OBSOLETE_PATTERNS.unusedCSS) || [];

  // Verificar se as classes são usadas nos componentes
  const componentsDir = path.join(PROJECT_ROOT, 'components');
  const allComponents = getAllFiles(componentsDir, ['.tsx', '.ts']);

  const usedClasses = new Set();
  allComponents.forEach(componentPath => {
    const componentContent = fs.readFileSync(componentPath, 'utf8');
    figmaClasses.forEach(figmaClass => {
      const className = figmaClass.replace('.', '');
      if (componentContent.includes(className)) {
        usedClasses.add(figmaClass);
      }
    });
  });

  const unusedClasses = figmaClasses.filter(cls => !usedClasses.has(cls));

  if (unusedClasses.length > 0) {
    issues.push({
      type: 'unused-css',
      message: `Classes CSS não utilizadas: ${unusedClasses.join(', ')}`,
      suggestions: ['Remover classes não utilizadas do CSS', 'Limpar código obsoleto'],
    });
  }

  return issues;
}

// Função para obter todos os arquivos
function getAllFiles(dir, extensions) {
  let files = [];
  const items = fs.readdirSync(dir);

  items.forEach(item => {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      files = files.concat(getAllFiles(fullPath, extensions));
    } else if (extensions.some(ext => item.endsWith(ext))) {
      files.push(fullPath);
    }
  });

  return files;
}

// Função principal
function main() {
  // console.log('🔍 Analisando código obsoleto...\n');

  const allIssues = [];

  // Debug: verificar caminhos
  // // console.log('DEBUG - PROJECT_ROOT:', PROJECT_ROOT);
  // // console.log('DEBUG - COMPONENTS_DIR:', COMPONENTS_DIR);
  // // console.log('DEBUG - CSS_FILE:', CSS_FILE);

  // Analisar componentes
  const componentsDir = path.join(PROJECT_ROOT, 'components');
  // // console.log('DEBUG - componentsDir:', componentsDir);
  // // console.log('DEBUG - Diretório existe?', fs.existsSync(componentsDir));

  const components = getAllFiles(componentsDir, ['.tsx', '.ts']);

  // console.log(`📁 Analisando ${components.length} componentes...`);
  // // console.log('DEBUG - Componentes encontrados:', components);

  components.forEach(componentPath => {
    const issues = analyzeFile(componentPath);
    if (issues.length > 0) {
      allIssues.push({
        file: path.relative(PROJECT_ROOT, componentPath),
        issues,
      });
    }
  });

  // Analisar CSS
  // console.log('🎨 Analisando CSS...');
  const cssIssues = analyzeCSS();
  if (cssIssues.length > 0) {
    allIssues.push({
      file: 'index.css',
      issues: cssIssues,
    });
  }

  // Relatório
  // console.log('\n📊 RELATÓRIO DE ANÁLISE\n');
  // console.log('='.repeat(50));

  if (allIssues.length === 0) {
    // console.log('✅ Nenhum problema encontrado! Código está limpo.');
  } else {
    allIssues.forEach(({ file, issues }) => {
      // console.log(`\n📄 ${file}`);
      // console.log('-'.repeat(file.length + 3));

      issues.forEach((issue, index) => {
        // console.log(`\n${index + 1}. ${issue.type.toUpperCase()}`);
        // console.log(`   ${issue.message}`);
        // console.log(`   💡 Sugestões:`);
        issue.suggestions.forEach(suggestion => {
          // console.log(`      - ${suggestion}`);
        });
      });
    });

    // console.log('\n' + '='.repeat(50));
    // console.log(`\n📈 RESUMO:`);
    // console.log(`   - ${allIssues.length} arquivo(s) com problemas`);
    // console.log(
      `   - ${allIssues.reduce((sum, { issues }) => sum + issues.length, 0)} problema(s) total`
    );

    // console.log('\n🛠️  PRÓXIMOS PASSOS:');
    // console.log('   1. Refatorar componentes usando design system');
    // console.log('   2. Remover classes CSS não utilizadas');
    // console.log('   3. Substituir espaçamentos hardcoded por tokens');
    // console.log('   4. Consolidar componentes duplicados');
  }
}

// Executar análise
if (
  import.meta.url.startsWith('file:') &&
  process.argv[1] &&
  import.meta.url.includes(process.argv[1].replace(/\\/g, '/'))
) {
  main();
} else {
  // Fallback: executar sempre quando chamado diretamente
  main();
}

export { analyzeFile, analyzeCSS, getAllFiles };
