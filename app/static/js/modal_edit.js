import { h } from 'https://unpkg.com/preact?module'
import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useState, useEffect } from 'https://unpkg.com/preact/hooks/dist/hooks.mjs?module'

import { Modal, ModalAction } from './modal.js'


export function EditModal (props) {
  const [title, setTitle] = useState(props.fileTitle)
  const updateTitle = event => setTitle(event.target.value)

  useEffect(() => {
    // update entered title when new edit modal is clicked
    setTitle(props.fileTitle)
  }, [props.fileName])

  return h(Modal, { actions: [
    new ModalAction('Cancel', ['outline', 'secondary']),
    new ModalAction('Update', ['primary'], {
      disabled: !title
    }),
  ], ...props }, html`
    <input
      type="hidden"
      id="file-name"
      name="file_name"
      value=${props.fileName} />

    <div class="custom-form-fieldgroup">
      <label for="document-title">Title<span class="required">*</span></label>
      <input
        type="text"
        class="form-control"
        id="document-title"
        name="document_title"
        value=${title}
        placeholder="Document name"
        required
        oninput=${updateTitle} />
    </div>

    <div class="custom-form-fieldgroup">
      <label for="document-description">Description (optional)</label>
      <textarea
        class="form-control"
        id="document-description"
        name="document_description"
        value=${props.fileDescription}
        placeholder="Let others know what this document is about..."
      ></textarea>
    </div>
  `)
}
