#!/usr/bin/env bash
# update-framework.sh — atualiza os ARQUIVOS DE FRAMEWORK de um repo instalado para uma
# tag-alvo do scaffold, sem tocar em conteúdo de produto (SPEC-003 de AYD-002).
#
# Contrato C3 (AYD-002): o repo instalado tem um `.framework-version` (na raiz, ou num
#   subdiretório imediato — ex.: docs/ — quando o template concentra tudo ali) declarando
#   framework/source/template/root/version/installed e a lista `files:` de globs de
#   framework. `root:` é o caminho relativo do diretório do manifesto até a raiz real do
#   repo (`.` quando o manifesto já está na raiz; `..` quando está um nível abaixo, ex.:
#   `docs/`). SÓ os paths cobertos por `files:` (relativos à raiz, não ao manifesto) são
#   elegíveis a diff/update; REQ/AYD/SPEC reais nunca.
#
# Uso:
#   update-framework.sh --to <ref> [--dry-run] [--from <git-url>] [--repo-root <path>]
#   update-framework.sh --check [--repo-root <path>]   # `files:` não casa conteúdo de produto?
#   update-framework.sh --help
#
# Mecânica: clona a tag-alvo (e, se possível, a versão atual como base) num tempdir e, para
# cada arquivo de framework da tag-alvo, decide criar/atualizar/conflito comparando
# base × working tree × alvo. Um conflito (arquivo editado localmente E mudado no upstream,
# ou base indisponível) NUNCA sobrescreve: grava a versão nova como `<arquivo>.framework-new`
# e para com exit ≠ 0. `--dry-run` só imprime o diff e não escreve nada.
set -euo pipefail

PROG="$(basename "$0")"
HERE="$(cd "$(dirname "$0")" && pwd)"
PARSER="$HERE/frontmatter.py"   # parser de frontmatter compartilhado (SPEC-001)

die() { echo "$PROG: $*" >&2; exit 1; }

usage() { sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; }

# ---- argumentos --------------------------------------------------------------
TARGET=""; FROM=""; REPO_ROOT=""; DRY_RUN=0; MODE="update"
while [ $# -gt 0 ]; do
  case "$1" in
    --to)        TARGET="${2:-}"; shift 2 ;;
    --from)      FROM="${2:-}"; shift 2 ;;
    --repo-root) REPO_ROOT="${2:-}"; shift 2 ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --check)     MODE="check"; shift ;;
    -h|--help)   usage; exit 0 ;;
    *)           die "argumento desconhecido: $1 (veja --help)" ;;
  esac
done

# ---- leitura do manifesto ----------------------------------------------------
mf_field() { sed -n "s/^$1:[[:space:]]*//p" "$2" | head -n1; }

# ---- localizar o manifesto e a raiz real do repo instalado --------------------
# `.framework-version` pode morar na raiz do repo ou num subdiretório imediato dela
# (ex.: docs/, quando o template concentra tudo ali) — a própria doc declara a
# distância até a raiz no campo `root:` (`.` ou `..`).
find_manifest_upward() {  # sobe de $1 procurando .framework-version; imprime o caminho
  d="$1"
  while [ "$d" != "/" ]; do
    [ -f "$d/.framework-version" ] && { printf '%s\n' "$d/.framework-version"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}
find_manifest_under() {  # busca .framework-version sob $1 (até 1 nível de subpasta)
  find "$1" -maxdepth 2 -name '.framework-version' 2>/dev/null | head -n1
}

if [ -n "$REPO_ROOT" ]; then
  ROOT="$(cd "$REPO_ROOT" && pwd)"
  MANIFEST="$(find_manifest_under "$ROOT")"
  [ -n "$MANIFEST" ] || die "sem .framework-version em $ROOT (nem em subpasta de 1 nível)"
else
  MANIFEST="$(find_manifest_upward "$HERE")" || die "não achei .framework-version subindo de $HERE (use --repo-root)"
fi

MDIR="$(dirname "$MANIFEST")"
ROOT_REL="$(mf_field root "$MANIFEST")"; ROOT_REL="${ROOT_REL:-.}"
# só "." (manifesto na raiz) e ".." (manifesto um nível abaixo, ex.: docs/) são suportados;
# usado para achar/validar a raiz real e, ao reescrever, preservar `root:` e excluir o
# próprio manifesto de files:.
case "$ROOT_REL" in
  .)  MANIFEST_REL=".framework-version" ;;
  ..) MANIFEST_REL="$(basename "$MDIR")/.framework-version" ;;
  *)  die "root: '$ROOT_REL' não suportado em $MANIFEST (use '.' ou '..')" ;;
esac
[ -n "$REPO_ROOT" ] || ROOT="$(cd "$MDIR/$ROOT_REL" && pwd)"

mf_globs() {  # imprime os globs da seção files: de um manifesto ($1)
  awk '
    /^files:[[:space:]]*$/ { inlist=1; next }
    inlist && /^[[:space:]]*-[[:space:]]*/ {
      line=$0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      sub(/[[:space:]]+#.*$/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (line != "") print line
      next
    }
    inlist && /^[^[:space:]#]/ { inlist=0 }
  ' "$1"
}

expand_globs() {  # $1=root diretório; globs no stdin → paths relativos de arquivos
  root="$1"
  while IFS= read -r glob; do
    [ -n "$glob" ] || continue
    case "$glob" in
      */\*\* | \*\*)
        dir="${glob%/**}"; [ "$dir" = "**" ] && dir="."
        [ -d "$root/$dir" ] && ( cd "$root" && find "$dir" -type f | sed 's#^\./##' )
        ;;
      *\**)
        echo "$PROG: glob não suportado (use literal ou 'dir/**'): $glob" >&2
        ;;
      *)
        [ -f "$root/$glob" ] && printf '%s\n' "$glob"
        ;;
    esac
  done
}

# ---- detecção de conteúdo de produto (reusa frontmatter.py da SPEC-001) -------
have_parser=0
if [ -f "$PARSER" ] && command -v python3 >/dev/null 2>&1; then have_parser=1; fi

is_product_doc() {  # $1=arquivo → 0 se for doc de produto REAL (tipo de produto + id sem NNN)
  case "$1" in *.md) ;; *) return 1 ;; esac
  [ "$have_parser" = 1 ] || return 1
  id="$(python3 "$PARSER" --field id "$1" 2>/dev/null || true)"
  [ -n "$id" ] || return 1
  case "$id" in *NNN*) return 1 ;; esac  # placeholder de template — não é produto
  type="$(python3 "$PARSER" --field type "$1" 2>/dev/null || true)"
  case "$type" in
    design|pdr|adr|spec|plan|tdr|requirements|roadmap|architecture) return 0 ;;
  esac
  return 1
}

# Verifica que nenhum glob de $manifest ($1) casa conteúdo de produto sob $root ($2).
# Retorna 0 se limpo, 1 se houver violação (paths violadores no stderr).
check_manifest() {
  _manifest="$1"; _root="$2"; _bad=0
  if [ "$have_parser" != 1 ]; then
    echo "$PROG: python3/frontmatter.py indisponível — checagem de manifesto pulada (fail-open)." >&2
    return 0
  fi
  for f in $(mf_globs "$_manifest" | expand_globs "$_root" | sort -u); do
    if is_product_doc "$_root/$f"; then
      echo "  ✗ $f casa conteúdo de produto e não pode entrar em files:" >&2
      _bad=1
    fi
  done
  return $_bad
}

# ---- modo --check ------------------------------------------------------------
if [ "$MODE" = "check" ]; then
  echo "Checando files: de ${MANIFEST} contra conteúdo de produto em ${ROOT}…"
  if check_manifest "$MANIFEST" "$ROOT"; then
    echo "✓ nenhum glob de framework casa conteúdo de produto."
    exit 0
  fi
  die "manifesto inválido: files: casa conteúdo de produto (veja acima)."
fi

# ---- modo update -------------------------------------------------------------
[ -n "$TARGET" ] || die "--to <ref> é obrigatório (veja --help)"

SOURCE="${FROM:-$(mf_field source "$MANIFEST")}"
TEMPLATE="$(mf_field template "$MANIFEST")"
CUR_VERSION="$(mf_field version "$MANIFEST")"
FRAMEWORK="$(mf_field framework "$MANIFEST")"
[ -n "$SOURCE" ]   || die "sem 'source:' no manifesto e sem --from — não sei de onde buscar"
[ -n "$TEMPLATE" ] || die "sem 'template:' no manifesto — não sei mapear os paths no scaffold"

command -v git >/dev/null 2>&1 || die "git é necessário e não foi encontrado no PATH"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

clone_ref() {  # $1=ref $2=destino → 0 se clonou
  git clone --quiet --depth 1 --branch "$1" "$SOURCE" "$2" >/dev/null 2>&1
}

# alvo (obrigatório)
if ! clone_ref "$TARGET" "$TMP/target"; then
  die "não consegui buscar a ref '$TARGET' de $SOURCE (tag inexistente ou sem rede) — nada aplicado"
fi
TROOT="$TMP/target/$TEMPLATE"
[ -d "$TROOT" ] || die "diretório de template '$TEMPLATE' não existe na ref '$TARGET'"
TMANIFEST="$(find_manifest_under "$TROOT")"
[ -n "$TMANIFEST" ] || die "'$TEMPLATE' na ref '$TARGET' não tem .framework-version (raiz ou 1 nível abaixo)"

# base (best-effort, para detectar edição local); tenta a versão atual com e sem 'v'
BROOT=""
for ref in "$CUR_VERSION" "v$CUR_VERSION"; do
  [ -n "$ref" ] || continue
  if clone_ref "$ref" "$TMP/base"; then
    [ -d "$TMP/base/$TEMPLATE" ] && BROOT="$TMP/base/$TEMPLATE"
    break
  fi
done
[ -n "$BROOT" ] || echo "$PROG: aviso — não achei a versão base '$CUR_VERSION' no source; tudo que diferir será tratado como conflito (nunca sobrescrevo sem base)." >&2

# guardrail AC-5: a lista files: da tag-alvo não pode casar conteúdo de produto
if ! check_manifest "$TMANIFEST" "$TROOT"; then
  die "manifesto da ref '$TARGET' inválido: files: casa conteúdo de produto — nada aplicado"
fi

# relativo do manifesto-alvo dentro de TROOT (mesma regra de root: usada para o local)
TROOT_REL="$(mf_field root "$TMANIFEST")"; TROOT_REL="${TROOT_REL:-.}"
case "$TROOT_REL" in
  .)  TMANIFEST_REL=".framework-version" ;;
  ..) TMANIFEST_REL="$(basename "$(dirname "$TMANIFEST")")/.framework-version" ;;
  *)  die "root: '$TROOT_REL' não suportado em $TMANIFEST (use '.' ou '..')" ;;
esac

# conjunto de arquivos de framework = files: da tag-alvo (a referência), menos o manifesto
TARGET_FILES="$(mf_globs "$TMANIFEST" | expand_globs "$TROOT" | grep -vxF "$TMANIFEST_REL" | sort -u || true)"
[ -n "$TARGET_FILES" ] || die "a ref '$TARGET' não declara arquivos de framework em files: — nada a fazer"

show_diff() {  # $1=dst (pode não existir) $2=src
  if [ -f "$1" ]; then
    git --no-pager diff --no-index -- "$1" "$2" || true
  else
    git --no-pager diff --no-index -- /dev/null "$2" || true
  fi
}

n_create=0; n_update=0; n_conflict=0; n_same=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  src="$TROOT/$rel"; dst="$ROOT/$rel"; base="$BROOT/$rel"
  if [ -f "$dst" ]; then
    if cmp -s "$src" "$dst"; then action="same"
    elif [ -n "$BROOT" ] && [ -f "$base" ] && cmp -s "$base" "$dst"; then action="update"
    else action="conflict"   # editado localmente e/ou sem base → nunca sobrescreve
    fi
  else
    action="create"
  fi

  case "$action" in
    same) n_same=$((n_same + 1)) ;;
    create)
      n_create=$((n_create + 1)); echo "  + $rel (novo)"
      if [ "$DRY_RUN" = 1 ]; then show_diff "$dst" "$src"
      else mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"; fi
      ;;
    update)
      n_update=$((n_update + 1)); echo "  ~ $rel"
      if [ "$DRY_RUN" = 1 ]; then show_diff "$dst" "$src"
      else cp "$src" "$dst"; fi
      ;;
    conflict)
      n_conflict=$((n_conflict + 1)); echo "  ! $rel (editado localmente — não sobrescrito)"
      if [ "$DRY_RUN" = 1 ]; then show_diff "$dst" "$src"
      else mkdir -p "$(dirname "$dst")"; cp "$src" "$dst.framework-new"
           echo "    → versão nova salva em $rel.framework-new (resolva à mão)"; fi
      ;;
  esac
done <<EOF
$TARGET_FILES
EOF

echo "-------------------------------------------------------------"
echo "framework $FRAMEWORK · $CUR_VERSION → $TARGET · template $TEMPLATE"
echo "novos:$n_create  atualizados:$n_update  conflitos:$n_conflict  inalterados:$n_same"

if [ "$DRY_RUN" = 1 ]; then
  echo "(dry-run: nada foi escrito no working tree)"
  exit 0
fi

if [ "$n_conflict" -gt 0 ]; then
  die "$n_conflict conflito(s): resolva os arquivos .framework-new e rode de novo — versão NÃO atualizada"
fi

# ---- atualiza o próprio manifesto: version/installed + files: da tag-alvo -----
# root: é preservado do manifesto local — descreve o layout deste repo instalado
# (onde o manifesto mora), não o da tag-alvo.
NEW_VERSION="${TARGET#v}"
{
  echo "# Manifesto do framework (contrato C3 de AYD-002)."
  echo "# version/installed são geridos por update-framework.sh — não edite à mão."
  echo "# files: lista os ARQUIVOS DE FRAMEWORK. Conteúdo de produto nunca entra aqui."
  echo "framework: $FRAMEWORK"
  echo "source: $SOURCE"
  echo "template: $TEMPLATE"
  echo "root: $ROOT_REL"
  echo "version: $NEW_VERSION"
  echo "installed: $(date +%F)"
  echo "files:"
  mf_globs "$TMANIFEST" | sed 's/^/  - /'
} > "$MANIFEST.tmp"
mv "$MANIFEST.tmp" "$MANIFEST"

echo "✓ framework atualizado para $NEW_VERSION ($(date +%F))."
