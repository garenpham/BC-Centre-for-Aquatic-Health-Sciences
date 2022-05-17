import { h } from 'https://unpkg.com/preact?module'
import { render } from 'https://unpkg.com/htm/preact/index.mjs?module'


export class ModalController {
  static openModal(Modal, props) {
    render(h(Modal, { shown: true, ...props }), document.body)
  }
}
