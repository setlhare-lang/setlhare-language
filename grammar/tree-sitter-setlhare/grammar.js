/**
 * @file Tree-sitter grammar for Setlhare
 * @author The Setlhare Authors
 * @license Apache-2.0
 *
 * STATUS: stub (v0.7 milestone). Mirrors docs/spec/02-syntax.md.
 *
 * To regenerate the parser:
 *   tree-sitter generate
 *   tree-sitter test
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'setlhare',

  extras: $ => [
    /\s/,
    $.line_comment,
    $.block_comment,
  ],

  word: $ => $.identifier,

  rules: {
    source_file: $ => repeat($._item),

    _item: $ => choice(
      $.import_decl,
      $.func_decl,
      // TODO: struct_decl, enum_decl, trait_decl, impl_block, actor_decl, const_decl, type_alias
    ),

    import_decl: $ => seq(
      'import',
      field('path', $.module_path),
      optional(seq('as', field('alias', $.identifier))),
    ),

    module_path: $ => seq($.identifier, repeat(seq('::', $.identifier))),

    func_decl: $ => seq(
      optional('pub'),
      'func',
      field('name', $.identifier),
      '(',
      optional(field('params', $.param_list)),
      ')',
      optional(seq('->', field('return_type', $._type))),
      field('body', choice($.block, seq('=>', $._expr))),
    ),

    param_list: $ => seq($.param, repeat(seq(',', $.param)), optional(',')),
    param: $ => seq(field('name', $.identifier), ':', field('type', $._type)),

    _type: $ => choice(
      $.identifier,
      // TODO: tuple, slice, array, borrow, optional, generic
    ),

    block: $ => seq('{', repeat($._stmt), optional($._expr), '}'),

    _stmt: $ => choice(
      $.let_stmt,
      $.expr_stmt,
      // TODO: assign_stmt, return_stmt, loop_stmt
    ),

    let_stmt: $ => choice(
      seq('let', optional('mut'), field('name', $.identifier), optional(seq(':', $._type)), '=', $._expr, ';'),
      seq(field('name', $.identifier), ':=', $._expr, ';'),
    ),

    expr_stmt: $ => seq($._expr, ';'),

    _expr: $ => choice(
      $.identifier,
      $.integer_literal,
      $.string_literal,
      $.bool_literal,
      // TODO: full expression grammar
    ),

    // ====== Tokens ======
    identifier: _ => /[a-zA-Z_][a-zA-Z0-9_]*/,
    integer_literal: _ => /[0-9][0-9_]*/,
    string_literal: _ => /"(?:[^"\\]|\\.)*"/,
    bool_literal: _ => choice('true', 'false'),

    line_comment: _ => token(seq('//', /[^\n]*/)),
    block_comment: _ => token(seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/')),
  },
});
