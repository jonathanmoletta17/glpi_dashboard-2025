#!/usr/bin/env node

/**
 * Script de auditoria para detectar código morto no projeto
 * Identifica arquivos não utilizados, imports não referenciados e componentes órfãos
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SRC_DIR = path.join(__dirname, '../src');
const COMPONENTS_DIR = path.join(SRC_DIR, 'components');

class DeadCodeAuditor {
  constructor() {
    this.allFiles = [];
    this.importMap = new Map();
    this.exportMap = new Map();
    this.deadCode = {
      unusedFiles: [],
      unusedExports: [],
      unusedImports: [],
      duplicateComponents: []
    };
  }

  // Coleta todos os arquivos TypeScript/JavaScript
  collectFiles(dir = SRC_DIR) {
    const files = fs.readdirSync(dir);

    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
        this.collectFiles(filePath);
      } else if (file.match(/\.(ts|tsx|js|jsx)$/)) {
        this.allFiles.push(filePath);
      }
    }
  }

  // Analisa imports e exports de um arquivo
  analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(SRC_DIR, filePath);

      // Detecta imports
      const importRegex = /import\s+(?:{[^}]+}|[^\s,]+|\*\s+as\s+\w+)\s+from\s+['"]([^'"]+)['"]/g;
      let match;

      while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1];
        if (!this.importMap.has(relativePath)) {
          this.importMap.set(relativePath, []);
        }
        this.importMap.get(relativePath).push(importPath);
      }

      // Detecta exports
      const exportRegex = /export\s+(?:default\s+)?(?:const|function|class|interface|type)\s+(\w+)/g;
      while ((match = exportRegex.exec(content)) !== null) {
        const exportName = match[1];
        if (!this.exportMap.has(relativePath)) {
          this.exportMap.set(relativePath, []);
        }
        this.exportMap.get(relativePath).push(exportName);
      }

    } catch (error) {
      console.warn(`Erro ao analisar ${filePath}: ${error.message}`);
    }
  }

  // Detecta arquivos não utilizados
  findUnusedFiles() {
    const referencedFiles = new Set();

    // Coleta todas as referências de imports
    for (const imports of this.importMap.values()) {
      for (const importPath of imports) {
        if (importPath.startsWith('.')) {
          referencedFiles.add(importPath);
        }
      }
    }

    // Verifica quais arquivos não são referenciados
    for (const filePath of this.allFiles) {
      const relativePath = path.relative(SRC_DIR, filePath);
      const isReferenced = Array.from(referencedFiles).some(ref => {
        const resolvedRef = path.resolve(path.dirname(filePath), ref);
        return resolvedRef.includes(relativePath.replace(/\.(ts|tsx)$/, ''));
      });

      // Ignora arquivos principais como main.tsx, App.tsx, etc.
      const isMainFile = relativePath.match(/(main|App|index)\.(ts|tsx)$/);

      if (!isReferenced && !isMainFile) {
        this.deadCode.unusedFiles.push(relativePath);
      }
    }
  }

  // Detecta componentes duplicados por similaridade de nome
  findDuplicateComponents() {
    const componentFiles = this.allFiles.filter(file =>
      file.includes('/components/') && file.match(/\.(tsx)$/)
    );

    const componentNames = componentFiles.map(file => {
      const name = path.basename(file, path.extname(file));
      return { name, file };
    });

    // Agrupa por similaridade de nome
    const groups = new Map();

    for (const { name, file } of componentNames) {
      const baseName = name.replace(/(List|Table|Chart|Card|Modal|Dialog)$/, '');
      if (!groups.has(baseName)) {
        groups.set(baseName, []);
      }
      groups.get(baseName).push({ name, file });
    }

    // Identifica grupos com múltiplos componentes
    for (const [baseName, components] of groups) {
      if (components.length > 1) {
        this.deadCode.duplicateComponents.push({
          baseName,
          components: components.map(c => path.relative(SRC_DIR, c.file))
        });
      }
    }
  }

  // Executa ESLint para detectar imports não utilizados
  checkUnusedImports() {
    try {
      execSync('npm run lint 2>&1', { encoding: 'utf8' });
    } catch (error) {
      const output = error.stdout || error.message;
      const unusedImportMatches = output.match(/.*unused-imports\/no-unused-imports.*/g);

      if (unusedImportMatches) {
        this.deadCode.unusedImports = unusedImportMatches.map(match => {
          const fileMatch = match.match(/([^\s]+\.tsx?)/);
          return fileMatch ? fileMatch[1] : match;
        });
      }
    }
  }

  // Gera relatório
  generateReport() {
    console.log('\n🔍 RELATÓRIO DE AUDITORIA DE CÓDIGO MORTO\n');
    console.log('=' .repeat(50));

    if (this.deadCode.unusedFiles.length > 0) {
      console.log('\n📁 ARQUIVOS NÃO UTILIZADOS:');
      this.deadCode.unusedFiles.forEach(file => {
        console.log(`  ❌ ${file}`);
      });
    }

    if (this.deadCode.duplicateComponents.length > 0) {
      console.log('\n🔄 COMPONENTES POTENCIALMENTE DUPLICADOS:');
      this.deadCode.duplicateComponents.forEach(group => {
        console.log(`  ⚠️  Grupo "${group.baseName}":`);
        group.components.forEach(comp => {
          console.log(`     - ${comp}`);
        });
      });
    }

    if (this.deadCode.unusedImports.length > 0) {
      console.log('\n📦 IMPORTS NÃO UTILIZADOS:');
      this.deadCode.unusedImports.forEach(imp => {
        console.log(`  ❌ ${imp}`);
      });
    }

    const totalIssues = this.deadCode.unusedFiles.length +
                       this.deadCode.duplicateComponents.length +
                       this.deadCode.unusedImports.length;

    console.log('\n' + '=' .repeat(50));
    console.log(`📊 RESUMO: ${totalIssues} problemas encontrados`);

    if (totalIssues === 0) {
      console.log('✅ Nenhum código morto detectado!');
    } else {
      console.log('\n💡 RECOMENDAÇÕES:');
      console.log('  1. Remova arquivos não utilizados');
      console.log('  2. Consolide componentes duplicados');
      console.log('  3. Execute "npm run lint:fix" para corrigir imports');
    }
  }

  // Executa auditoria completa
  async run() {
    console.log('🚀 Iniciando auditoria de código morto...');

    this.collectFiles();
    console.log(`📂 Analisando ${this.allFiles.length} arquivos...`);

    for (const file of this.allFiles) {
      this.analyzeFile(file);
    }

    this.findUnusedFiles();
    this.findDuplicateComponents();
    this.checkUnusedImports();

    this.generateReport();
  }
}

// Executa se chamado diretamente
if (require.main === module) {
  const auditor = new DeadCodeAuditor();
  auditor.run().catch(console.error);
}

module.exports = DeadCodeAuditor;
