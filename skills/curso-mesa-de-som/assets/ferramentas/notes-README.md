# Notas do apresentador

Cada arquivo `notes/<id>.html` é a nota do slide `<id>` do deck (`07-slides/index.html`). O gerador (`tools/build_slides.py`, função `hooknotes`) põe o conteúdo do arquivo dentro do `<aside class="notes">` do slide e descarta a nota gerada. Todo slide do deck tem o seu arquivo (144 hoje); nota de slide removido sai da pasta.

O conteúdo é HTML simples: parágrafos `<p>` e, quando houver, o bloco da pergunta à turma.

## Política

1. **A nota complementa o slide; não repete.** Nada do texto visível do slide nem do texto do diagrama entra na nota. Se está no slide, o professor lê no slide.
2. **A nota traz o que o professor fala além do slide:**
   - o porquê de cada regra;
   - o caminho na mesa (menus, botões, encoders) quando o slide só dá a ideia;
   - as nuances entre modelos e famílias;
   - onde há abordagens diferentes: todas as opções, com efeito e contexto, sem dizer quem pensa assim e sem tomar lado, no bloco único `<div class="divn"><b>Abordagens divergentes:</b> … <br><b>A</b> … <br><b>B</b> …</div>` (o `build_slides.py` aplica o estilo inline, constante `DIVN`);
   - o erro comum e como reconhecer;
   - a transição para o próximo slide ou capítulo.
3. **Pergunta à turma: só na nota, no topo, em destaque.** O slide não mostra pergunta. Na nota, ela vem num bloco com estilo inline, porque a janela do apresentador do reveal não carrega o CSS do deck:

   ```html
   <div style="background:#3a2a00;border-left:4px solid #ffb020;padding:6px 10px;margin:0 0 8px;color:#ffd27a"><b>Pergunte à turma:</b> …</div>
   ```

4. **Nota de quiz:** por que cada alternativa errada está errada, qual slide retomar se a turma errar e a ponte para o próximo capítulo.
5. **Proibido na nota:** "Em cena" ou qualquer cena fictícia; X16/X12; "Texto do diagrama"; metacomentário de produção (pesquisa, agentes, arquivos de origem, lista do curso, justificativa de escolhas do material). Nomes de professores, autores, escolas, cursos, canais, fóruns ou lojas como fonte; documento do fabricante só de forma genérica ("manual oficial", "exemplo do fabricante").
6. **"(não confirmado)"** continua valendo como convenção técnica: nem o manual nem a prática comprovam aquilo; o alerta é "⚠ Confira na sua mesa".

## Conferência

```
python3 -I tools/check_notes.py 07-slides/index.html     # acusa nota vazia, nota que repete o slide/diagrama e termo proibido
python3 -I tools/check_notes.py --selftest
```

Uma nota "repete o slide" quando mais de 35% das trincas de palavras dela estão no texto visível ou no diagrama do slide, ou quando uma frase dela (6+ palavras) está 80% contida no slide.

## Como escrever uma nota nova

Crie `notes/<id>.html` (o id aparece na URL do slide, depois de `#/`), siga a política acima, rode `python3 -I tools/build_slides.py` e depois `check_notes.py`.
