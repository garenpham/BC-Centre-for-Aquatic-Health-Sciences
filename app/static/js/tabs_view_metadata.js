import cc from 'https://unpkg.com/classcat?module';
import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useReducer, useRef } from 'https://unpkg.com/preact/hooks/dist/hooks.mjs?module'
import { TabView } from './tab_view.js'
import { TabsView } from './tabs_view.js'


// a simple patch reducer for collapsing payload into a new state
const patch = (state, payload) =>
  Object.assign({}, state, payload)

// converts SQL date format to YYYY-MM-DD
const toYYYYMMDD = (sqlDate) =>
  new Date(sqlDate).toISOString().split("T")[0]

// posts the given form to the given endpoint with callback(category, message)
const postFormData = (endpoint, form, callback) => {
  if (!form.reportValidity()) {
    return
  }

  fetch(endpoint, {
    method: 'POST',
    body: new FormData(form)
  })
    .then(response => response.json())
    .then(({ category, message }) => {
      callback(category, message)
      form.reset()
    })
}


const EnvironmentalDataTabView = (props) => {
  const [state, dispatch] = useReducer(patch, {
    dateCollected: null,
    submissionNo: '',
    hatcheryId: '',
    samplers: '',
    waterTemperature: null,
    oxygen: null,
    saturation: null,
    fishSwabs: null,
    biofilmSwabs: null,
    waterSamples: null,
    waterVolPerSample: null,
    isExistingData: false,
  })

  const loadExistingEnvironmentalData = () => {
    if (!state.submissionNo) {
      return props.onmessage('danger', 'Failed to load submission data:'
        + ' Cannot load data with empty submission number')
    }

    fetch(`/environmental_data/${state.submissionNo}`)
      .then(response => response.json())
      .then(environmentalData => {
        dispatch({
          ...environmentalData,
          dateCollected: toYYYYMMDD(environmentalData.dateCollected),
          isExistingData: true,
        })
        props.onmessage('info', `Loaded submission '${state.submissionNo}' successfully`)
      })
      .catch(err => {
        console.error(err)
        props.onmessage('danger', 'Failed to load submission data:'
          + ` Submission '${state.submissionNo}' does not exist`)
      })
  }

  const formRef = useRef(null)
  const submitEnvironmentalData = () =>
    postFormData('/update_environmental_data', formRef.current, props.onmessage)

  return html`
    <form ref=${formRef} class="custom-form needs-validation">

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="date"
            class="form-control"
            id="date-collected"
            name="date_collected"
            value=${state.dateCollected}
            required />
          <label for="date-collected">Date collected</label>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <label for="submission-no">CAHS Submission Number<span class="required">*</span></label>
          <div class="custom-form-fieldwrap">
            <input
              type="text"
              class="form-control"
              id="submission-no"
              name="CAHS_Submission_Number_submission_data"
              value=${state.submissionNo}
              placeholder="V0123"
              required
              oninput=${event => dispatch({
                submissionNo: event.target.value,
                isExistingData: false,
              })} />

            <button
              type="button"
              class="btn btn-primary"
              onclick=${loadExistingEnvironmentalData}
            >Load existing data</button>
          </div>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <select
            class="form-control"
            id="hatchery-name"
            name="location_id_submission"
            value=${state.hatcheryId}
            required>
            <option value="">(None selected)</option>
            ${Object.entries(window.CAHS.hatcheries).map(([hatcheryId, hatcheryName]) => html`
              <option value=${hatcheryId}>${hatcheryName}</option>
            `)}
          </select>
          <label for="hatchery-name">Hatchery name</label>
        </div>
      </div>

      <div class="custom-form-fieldgroup">
        <input
          type="text"
          class="form-control"
          id="samplers"
          name="Samplers"
          value=${state.samplers}
          placeholder="e.g. John Doe, Jane Doe"
          required />
        <label for="samplers">Samplers</label>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="number"
            step="0.1"
            class="form-control"
            id="water-temperature"
            name="water_temp"
            value=${state.waterTemperature}
            placeholder="10.0" />
          <label for="water-temperature">Water temperature (ºC)</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="0.01"
            class="form-control"
            id="oxygen"
            name="oxygen_measurement"
            value=${state.oxygen}
            placeholder="10.00" />
          <label for="oxygen">Oxygen (mg/L)</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            max="100"
            step="0.1"
            class="form-control"
            id="saturation"
            name="saturation_percent"
            value=${state.saturation}
            placeholder="100.0" />
          <label for="saturation">Saturation (%)</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="5"
            class="form-control"
            id="water-vol-per-sample"
            name="vol_water"
            value=${state.waterVolPerSample}
            placeholder="1000" />
          <label for="water-vol-per-sample">Vol. water/sample (mL)</label>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="1"
            class="form-control"
            id="water-samples"
            name="num_water_samples_collected"
            value=${state.waterSamples}
            placeholder="0"
            required />
          <label for="water-samples"># water samples collected</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="1"
            class="form-control"
            id="fish-swabs"
            name="num_fish_swabs"
            value=${state.fishSwabs}
            placeholder="0"
            required />
          <label for="fish-swabs"># fish swabs</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="1"
            class="form-control"
            id="biofilm-swabs"
            name="num_biofilm_swabs"
            value=${state.biofilmSwabs}
            placeholder="0"
            required />
          <label for="biofilm-swabs"># biofilm swabs</label>
        </div>
      </div>

      <div class="custom-form-actions">
        <button
          type="button"
          class="btn btn-primary"
          onclick=${submitEnvironmentalData}
        >${state.isExistingData
          ? `Update submission '${state.submissionNo}'`
          : "Add environmental data"
        }</button>
      </div>
    </form>
  `
}

const SampleDataTabView = (props) => {
  const [state, dispatch] = useReducer(patch, {
    sampleId: '',
    submissionNo: '',
    sampleType: '',
    sampleLocation: '',
    fishWeight: null,
    fishLength: null,
    biofilmMaterial: '',
    waterDateFiltered: null,
    waterVolFiltered: null,
    waterTimeToFilter: '',
    isExistingData: false,
  })

  const loadExistingSampleData = () => {
    if (!state.sampleId) {
      return props.onmessage('danger', 'Failed to load sample data:'
        + ' Cannot load data with empty sample ID')
    }

    fetch(`/sample_data/${state.sampleId}`)
      .then(response => response.json())
      .then(sampleData => {
        dispatch({
          ...sampleData,
          waterDateFiltered: toYYYYMMDD(sampleData.waterDateFiltered),
          isExistingData: true,
        })
        props.onmessage('info', `Loaded sample '${state.sampleId}' successfully`)
      })
      .catch(err => {
        console.error(err)
        props.onmessage('danger', 'Failed to load sample data:'
          + ` Sample '${state.sampleId}' does not exist`)
      })
  }

  const formRef = useRef(null)
  const submitSampleData = () =>
    postFormData('/update_sample_data', formRef.current, props.onmessage)

  return html`
    <form ref=${formRef} class="custom-form needs-validation">

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <label for="sample-id">Sample ID<span class="required">*</span></label>
          <div class="custom-form-fieldwrap">
            <input
              type="text"
              class="form-control"
              id="sample-id"
              name="sample_id"
              value=${state.sampleId}
              placeholder="SBio123"
              required
              oninput=${event => dispatch({
                sampleId: event.target.value,
                isExistingData: false,
              })} />

            <button
              type="button"
              class="btn btn-primary"
              onclick=${loadExistingSampleData}
            >Load existing data</button>
          </div>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="text"
            class="form-control"
            id="submission-no"
            name="CAHS_Submission_Number"
            value=${state.submissionNo}
            placeholder="V0123"
            required />
          <label for="submission-no">CAHS Submission Number</label>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <select
            class="form-control"
            id="sample-type"
            name="sample_Type"
            value=${state.sampleType}
            required>
            <option value="">(None selected)</option>
            <option value="Biofilm swab">Biofilm swab</option>
            <option value="Fish swab">Fish swab</option>
            <option value="Water filter">Water filter</option>
          </select>
          <label for="sample-type">Sample type</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="text"
            class="form-control"
            id="sample-location"
            name="sample_Location"
            value=${state.sampleLocation}
            placeholder="e.g. Pond 5"
            required />
          <label for="sample-location">Sample location</label>
        </div>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="0.01"
            class="form-control"
            id="fish-weight"
            name="fish_weight"
            value=${state.fishWeight}
            placeholder="10.00" />
          <label for="fish-weight">Fish weight (g)</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="1"
            class="form-control"
            id="fish-length"
            name="fish_Length"
            value=${state.fishLength}
            placeholder="100" />
          <label for="fish-length">Fish length (mm)</label>
        </div>
      </div>

      <div class="custom-form-fieldgroup">
        <input
          type="text"
          class="form-control"
          id="biofilm-material"
          name="material_swab"
          value=${state.biofilmMaterial}
          placeholder="e.g. Concrete wall" />
        <label for="biofilm-material">Material swabbed for biofilm</label>
      </div>

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="date"
            class=${cc([
              "form-control",  // HACK: CSS doesn't have a selector for empty optional date inputs
              ...(!state.waterDateFiltered ? ["invalid"] : ["valid"]),
            ])}
            id="water-date-filtered"
            name="date_filtered"
            value=${state.waterDateFiltered}
            placeholder="test"
            oninput=${event => dispatch({ waterDateFiltered: event.target.value })} />
          <label for="water-date-filtered">Date filtered</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="5"
            class="form-control"
            id="water-vol-filtered"
            name="volume_filtered"
            value=${state.waterVolFiltered}
            placeholder="1000" />
          <label for="water-vol-filtered">Vol. filtered (mL)</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="text"
            class="form-control"
            id="water-time-to-filter"
            name="time_to_filter"
            value=${state.waterTimeToFilter}
            placeholder="0:00:00" />
          <label for="water-time-to-filter">Time to filter (h:mm:ss)</label>
        </div>
      </div>

      <div class="custom-form-actions">
        <button
          type="button"
          class="btn btn-primary"
          onclick=${submitSampleData}
        >${state.isExistingData
          ? `Update sample '${state.sampleId}'`
          : "Add sample data"
        }</button>
      </div>
    </form>
  `
}

const HatcheryDataTabView = (props) => {
  const formRef = useRef(null)
  const submitHatcheryData = () =>
    postFormData('/update_hatchery_data', formRef.current, props.onmessage)

  return html`
    <form ref=${formRef} class="custom-form needs-validation">

      <div class="custom-form-fieldrow">
        <div class="custom-form-fieldgroup">
          <input
            type="number"
            min="0"
            step="1"
            class="form-control"
            id="hatchery-id"
            name="location_id"
            placeholder="123"
            required />
          <label for="hatchery-id">Hatchery ID</label>
        </div>

        <div class="custom-form-fieldgroup">
          <input
            type="text"
            class="form-control"
            id="hatchery-name"
            name="location_name"
            placeholder="Hatchery X"
            required />
          <label for="hatchery-name">Hatchery name</label>
        </div>
      </div>

      <div class="custom-form-actions">
        <button
          type="button"
          class="btn btn-primary"
          onclick=${submitHatcheryData}
        >Upload hatchery data</button>
      </div>
    </form>
  `
}


export function MetadataTabsView (props) {
  return html`
    <${TabsView} tab=${props.tab}>
      <${TabView} id="environmental-data" name="Environmental data">
        <${EnvironmentalDataTabView} onmessage=${props.onmessage} />
      </${TabView}>

      <${TabView} id="sample-data" name="Sample data">
        <${SampleDataTabView} onmessage=${props.onmessage} />
      </${TabView}>

      <${TabView} id="hatchery-data" name="Hatchery data">
        <${HatcheryDataTabView} onmessage=${props.onmessage} />
      </${TabView}>
    </${TabsView}>
  `
}
