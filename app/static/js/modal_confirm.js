import { h } from 'https://unpkg.com/preact?module'
import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'

import { Modal, ModalAction } from './modal.js'


export function ConfirmModal (props) {
  return h(Modal, { actions: [
    new ModalAction('OK', ['primary']),
    new ModalAction('Cancel', ['outline', 'secondary']),
  ], ...props }, [html`
    <p>${props.body}</p>
  `])
}
