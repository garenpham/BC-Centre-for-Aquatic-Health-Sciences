import { h } from 'https://unpkg.com/preact?module'
import { html, render } from 'https://unpkg.com/htm/preact/index.mjs?module'


export function Alert (props) {
  return html`
    <div class="alert alert-dismissible alert-${props.category}" role="alert">
      ${props.message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">×</span>
      </button>
    </div>
  `
}

export function renderAlert ({ category, message }, element) {
  render(h(Alert, { category, message }), element)
}
