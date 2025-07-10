#!/usr/bin/env node

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import yargs from 'yargs/yargs';
import { hideBin } from 'yargs/helpers';
import { rawWork } from './worker';
import { Context } from './lib/Context';
import { Compiler } from './lib/Compiler';
import { Parser } from './lib/Parser';
import { defaultCompilerOptions } from './lib/Compiler';
import { RenderOptions } from './lib/Element';

// Initialize global context
const globalContext = new Context();
const initPath = join(__dirname, '../src/lib/init.btx');
if (existsSync(initPath)) {
  Compiler.compile(Parser.parse(readFileSync(initPath).toString()), globalContext);
}

async function main() {
  const argv = yargs(hideBin(process.argv))
    .option('input', {
      alias: 'i',
      describe: 'Input btex file',
      type: 'string',
      demandOption: true,
    })
    .option('output', {
      alias: 'o',
      describe: 'Output HTML file',
      type: 'string',
      demandOption: true,
    })
    .option('preamble', {
      alias: 'p',
      describe: 'Preamble file (optional)',
      type: 'string',
    })
    .option('inline', {
      describe: 'Inline mode',
      type: 'boolean',
      default: false,
    })
    .option('equation-mode', {
      describe: 'Equation mode',
      type: 'boolean',
      default: false,
    })
    .option('inverse-search', {
      describe: 'Enable inverse search',
      type: 'boolean',
      default: false,
    })
    .option('css', {
      describe: 'Include KaTeX CSS in output',
      type: 'boolean',
      default: true,
    })
    .option('title', {
      describe: 'HTML title',
      type: 'string',
      default: 'bTeX Output',
    })
    .help()
    .alias('help', 'h')
    .version()
    .alias('version', 'v')
    .parseSync();

  try {
    // Read input file
    if (!existsSync(argv.input)) {
      console.error(`Error: Input file '${argv.input}' does not exist.`);
      process.exit(1);
    }

    const inputCode = readFileSync(argv.input, 'utf-8');
    
    // Read preamble if provided
    let preamble: string | undefined;
    if (argv.preamble) {
      if (!existsSync(argv.preamble)) {
        console.error(`Error: Preamble file '${argv.preamble}' does not exist.`);
        process.exit(1);
      }
      preamble = readFileSync(argv.preamble, 'utf-8');
    }

    // Prepare options
    const options = { ...defaultCompilerOptions };
    options.inline = argv.inline;
    options.equationMode = argv.equationMode;

    const renderOptions: RenderOptions = {
      inverseSearch: argv.inverseSearch,
    };

    // Process the btex code
    console.log(`Processing ${argv.input}...`);
    const result = await rawWork({
      code: inputCode,
      preamble,
      options,
      renderOptions,
      globalContext,
      taskId: 0,
    });

    // Check for errors
    if (result.errors.length > 0) {
      console.error('Compilation errors:');
      result.errors.forEach(error => console.error(`  ${error}`));
      process.exit(1);
    }

    // Generate HTML output
    let htmlOutput = result.html;
    
    if (argv.css) {
      const katexCss = 'https://cdn.jsdelivr.net/npm/katex@0.15.6/dist/katex.min.css';
      htmlOutput = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${argv.title}</title>
    <link rel="stylesheet" href="${katexCss}">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 2em; }
        .math { margin: 1em 0; }
        .math-display { text-align: center; margin: 1em 0; }
        .math-inline { display: inline; }
    </style>
</head>
<body>
${htmlOutput}
</body>
</html>`;
    }

    // Write output file
    writeFileSync(argv.output, htmlOutput, 'utf-8');
    console.log(`Successfully compiled to ${argv.output}`);

    // Show warnings if any
    if (result.warnings.length > 0) {
      console.warn('Warnings:');
      result.warnings.forEach(warning => console.warn(`  ${warning}`));
    }

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
} 