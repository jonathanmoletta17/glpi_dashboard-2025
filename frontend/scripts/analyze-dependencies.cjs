const fs = require('fs');
const path = require('path');

/**
 * Script para análise de dependências não utilizadas
 * Verifica package.json vs imports reais no código
 */

class DependencyAnalyzer {
  constructor() {
    this.projectRoot = process.cwd();
    this.packageJsonPath = path.join(this.projectRoot, 'package.json');
    this.srcPath = path.join(this.projectRoot, 'src');
    this.usedDependencies = new Set();
    this.packageJson = null;
  }

  /**
   * Verifica se é um módulo builtin do Node.js
   */
  isNodeBuiltin(moduleName) {
    const builtins = [
      'fs', 'path', 'url', 'util', 'os', 'crypto', 'http', 'https',
      'stream', 'events', 'buffer', 'querystring', 'zlib', 'child_process',
      'cluster', 'dgram', 'dns', 'net', 'readline', 'repl', 'tls', 'tty',
      'vm', 'worker_threads', 'assert', 'constants', 'module', 'perf_hooks',
      'process', 'punycode', 'string_decoder', 'timers', 'trace_events',
      'v8', 'wasi'
    ];
    return builtins.includes(moduleName.split('/')[0]);
  }

  /**
   * Carrega o package.json
   */
  loadPackageJson() {
    try {
      const content = fs.readFileSync(this.packageJsonPath, 'utf8');
      this.packageJson = JSON.parse(content);
      return true;
    } catch (error) {
      console.error('❌ Erro ao carregar package.json:', error.message);
      return false;
    }
  }

  /**
   * Coleta todos os arquivos TypeScript/JavaScript
   */
  collectSourceFiles(dir = this.srcPath) {
    const files = [];

    if (!fs.existsSync(dir)) {
      console.warn(`⚠️  Diretório não encontrado: ${dir}`);
      return files;
    }

    const items = fs.readdirSync(dir);

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        // Pular node_modules e outros diretórios irrelevantes
        if (!['node_modules', '.git', 'dist', 'build', 'coverage'].includes(item)) {
          files.push(...this.collectSourceFiles(fullPath));
        }
      } else if (stat.isFile()) {
        // Incluir apenas arquivos de código
        if (/\.(ts|tsx|js|jsx)$/.test(item)) {
          files.push(fullPath);
        }
      }
    }

    return files;
  }

  /**
   * Analisa imports em um arquivo
   */
  analyzeFileImports(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const imports = [];

      // Regex para diferentes tipos de import
      const importPatterns = [
        // import { something } from 'package'
        /import\s+{[^}]*}\s+from\s+['"]([^'"]+)['"]/g,
        // import something from 'package'
        /import\s+\w+\s+from\s+['"]([^'"]+)['"]/g,
        // import * as something from 'package'
        /import\s+\*\s+as\s+\w+\s+from\s+['"]([^'"]+)['"]/g,
        // import 'package'
        /import\s+['"]([^'"]+)['"]/g,
        // require('package')
        /require\(['"]([^'"]+)['"]\)/g,
        // dynamic import()
        /import\(['"]([^'"]+)['"]\)/g
      ];

      for (const pattern of importPatterns) {
        let match;
        while ((match = pattern.exec(content)) !== null) {
          const importPath = match[1];

          // Filtrar apenas dependências externas (não caminhos relativos, aliases ou módulos internos)
          if (!importPath.startsWith('.') &&
              !importPath.startsWith('/') &&
              !importPath.startsWith('@/') && // Path aliases
              !this.isNodeBuiltin(importPath)) {
            // Extrair nome do pacote (remover subpaths)
            const packageName = importPath.startsWith('@')
              ? importPath.split('/').slice(0, 2).join('/') // @scope/package
              : importPath.split('/')[0]; // package

            imports.push(packageName);
            this.usedDependencies.add(packageName);
          }
        }
      }

      return imports;
    } catch (error) {
      console.warn(`⚠️  Erro ao analisar ${filePath}:`, error.message);
      return [];
    }
  }

  /**
   * Analisa todos os arquivos do projeto
   */
  analyzeProject() {
    console.log('🔍 Coletando arquivos do projeto...');
    const sourceFiles = this.collectSourceFiles();
    console.log(`📁 Encontrados ${sourceFiles.length} arquivos de código`);

    console.log('\n🔍 Analisando imports...');
    for (const file of sourceFiles) {
      this.analyzeFileImports(file);
    }

    console.log(`📦 Encontradas ${this.usedDependencies.size} dependências únicas em uso`);
  }

  /**
   * Compara dependências declaradas vs utilizadas
   */
  findUnusedDependencies() {
    const { dependencies = {}, devDependencies = {} } = this.packageJson;
    const allDeclared = { ...dependencies, ...devDependencies };
    const declaredPackages = Object.keys(allDeclared);

    const unused = [];
    const missing = [];

    // Encontrar dependências não utilizadas
    for (const declared of declaredPackages) {
      if (!this.usedDependencies.has(declared)) {
        // Verificar se é uma dependência de build/dev que pode não aparecer no código
        const buildTools = [
          'vite', 'webpack', 'rollup', 'parcel',
          'typescript', 'eslint', 'prettier', 'husky', 'lint-staged',
          'vitest', 'jest', '@testing-library',
          '@types/', '@typescript-eslint/',
          'tailwindcss', 'postcss', 'autoprefixer'
        ];

        const isBuildTool = buildTools.some(tool =>
          declared.includes(tool) || declared.startsWith(tool)
        );

        if (!isBuildTool) {
          unused.push({
            name: declared,
            version: allDeclared[declared],
            type: dependencies[declared] ? 'dependency' : 'devDependency'
          });
        }
      }
    }

    // Encontrar dependências utilizadas mas não declaradas
    for (const used of this.usedDependencies) {
      if (!declaredPackages.includes(used)) {
        missing.push(used);
      }
    }

    return { unused, missing };
  }

  /**
   * Gera relatório de análise
   */
  generateReport() {
    const { unused, missing } = this.findUnusedDependencies();

    console.log('\n' + '='.repeat(60));
    console.log('📊 RELATÓRIO DE ANÁLISE DE DEPENDÊNCIAS');
    console.log('='.repeat(60));

    // Dependências não utilizadas
    if (unused.length > 0) {
      console.log('\n❌ DEPENDÊNCIAS NÃO UTILIZADAS:');
      console.log('-'.repeat(40));

      unused.forEach(dep => {
        console.log(`  📦 ${dep.name} (${dep.version}) - ${dep.type}`);
      });

      console.log('\n💡 RECOMENDAÇÕES:');
      console.log('  • Remover dependências não utilizadas para reduzir bundle size');
      console.log('  • Executar: npm uninstall ' + unused.map(d => d.name).join(' '));
    } else {
      console.log('\n✅ Nenhuma dependência não utilizada encontrada!');
    }

    // Dependências faltantes
    if (missing.length > 0) {
      console.log('\n⚠️  DEPENDÊNCIAS UTILIZADAS MAS NÃO DECLARADAS:');
      console.log('-'.repeat(40));

      missing.forEach(dep => {
        console.log(`  📦 ${dep}`);
      });

      console.log('\n💡 RECOMENDAÇÕES:');
      console.log('  • Adicionar dependências faltantes ao package.json');
      console.log('  • Executar: npm install ' + missing.join(' '));
    } else {
      console.log('\n✅ Todas as dependências utilizadas estão declaradas!');
    }

    // Estatísticas
    console.log('\n📈 ESTATÍSTICAS:');
    console.log('-'.repeat(40));
    const { dependencies = {}, devDependencies = {} } = this.packageJson;
    console.log(`  📦 Dependências declaradas: ${Object.keys(dependencies).length}`);
    console.log(`  🔧 DevDependências declaradas: ${Object.keys(devDependencies).length}`);
    console.log(`  ✅ Dependências em uso: ${this.usedDependencies.size}`);
    console.log(`  ❌ Dependências não utilizadas: ${unused.length}`);
    console.log(`  ⚠️  Dependências faltantes: ${missing.length}`);

    // Economia potencial
    if (unused.length > 0) {
      console.log('\n💰 ECONOMIA POTENCIAL:');
      console.log('-'.repeat(40));
      console.log(`  • ${unused.length} pacotes podem ser removidos`);
      console.log('  • Redução no bundle size');
      console.log('  • Instalação mais rápida');
      console.log('  • Menos vulnerabilidades potenciais');
    }

    console.log('\n' + '='.repeat(60));

    return { unused, missing };
  }

  /**
   * Executa análise completa
   */
  run() {
    console.log('🚀 Iniciando análise de dependências...');

    if (!this.loadPackageJson()) {
      process.exit(1);
    }

    this.analyzeProject();
    const results = this.generateReport();

    // Exit code baseado nos resultados
    if (results.unused.length > 0 || results.missing.length > 0) {
      console.log('\n⚠️  Problemas encontrados. Verifique as recomendações acima.');
      process.exit(1);
    } else {
      console.log('\n✅ Análise concluída. Nenhum problema encontrado!');
      process.exit(0);
    }
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  const analyzer = new DependencyAnalyzer();
  analyzer.run();
}

module.exports = DependencyAnalyzer;
