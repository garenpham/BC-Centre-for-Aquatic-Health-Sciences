import cc from 'https://unpkg.com/classcat?module'
import { h } from 'https://unpkg.com/preact?module'
import { html, render, Component } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useState } from 'https://unpkg.com/preact/hooks/dist/hooks.mjs?module'

import { Modal, ModalAction } from './modal.js'


function FileInput(props) {
  return html`
    <div class="custom-modal-fieldgroup">
      <label for="file-input">File<span class="required">*</span></label>
      <div class="file-input">
        <label for="file-input" class="btn btn-primary">Choose file</label>
        <span class="file-name">${props.value || 'No file chosen'}</span>
      </div>
      <input
        hidden
        type="file"
        id="file-input"
        name="file"
        required
        onchange=${props.onchange} />
    </div>
  `
}

export function UploadSampleModal(props) {
  const [id, setId] = useState('')
  const updateId = event => setId(event.target.value)

  const [file, setFile] = useState('')
  const [fileSize, setFileSize] = useState(0)
  const updateFile = event => {
    const file = event.target.files[0]
    if (file) {
      setFile(file.name)
      setFileSize(file.size)
    }
  }

  return h(Modal, { actions: [
    new ModalAction('Cancel', ['outline', 'secondary']),
    new ModalAction('Upload', ['primary'], {
      disabled: !id || !file
    }),
  ], ...props }, html`
    <input
      type="hidden"
      name="file_size"
      value=${fileSize} />

    <input
      type="hidden"
      name="file_type"
      value="sample" />

    <div class="custom-modal-fieldrow">
      <div class="custom-modal-fieldgroup">
        <label for="sample-id">Sample ID<span class="required">*</span></label>
        <input
          type="text"
          class="form-control"
          id="sample-id"
          name="sample_id"
          placeholder="SBio123"
          required
          oninput=${updateId} />
      </div>
      <${FileInput} value=${file || 'No file chosen'} onchange=${updateFile} />
    </div>
  `)
}

export function UploadDocumentModal(props) {
  const [title, setTitle] = useState('')
  const updateTitle = event => setTitle(event.target.value)

  const [file, setFile] = useState('')
  const [fileSize, setFileSize] = useState(0)
  const updateFile = event => {
    const file = event.target.files[0]
    if (file) {
      setFile(file.name)
      setFileSize(file.size)
    }
  }

  return h(Modal, { actions: [
    new ModalAction('Cancel', ['outline', 'secondary']),
    new ModalAction('Upload', ['primary'], {
      disabled: !title || !file
    }),
  ], ...props }, html`
    <input
      type="hidden"
      name="file_size"
      value=${fileSize} />

    <input
      type="hidden"
      name="file_type"
      value="document" />

    <div class="custom-modal-fieldrow">
      <div class="custom-modal-fieldgroup">
        <label for="file-title">Title<span class="required">*</span></label>
        <input
          type="text"
          class="form-control"
          id="document-title"
          name="document_title"
          placeholder="Document name"
          required
          oninput=${updateTitle} />
      </div>
      <${FileInput} value=${file || 'No file chosen'} onchange=${updateFile} />
    </div>

    <div class="custom-modal-fieldgroup">
      <label for="document-description">Description (optional)</label>
      <textarea
        class="form-control"
        id="document-description"
        name="document_description"
        placeholder="Let others know what this file is about..."
      ></textarea>
    </div>
  `)
}
