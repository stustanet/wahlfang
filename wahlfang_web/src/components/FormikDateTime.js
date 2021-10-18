import Datetime from 'react-datetime';
import moment from 'moment';
import "react-datetime/css/react-datetime.css";

const DATE_FORMAT = 'DD-MM-YYYY HH:mm'

const FormikDateTime = ({ field, form, timeFormat }) => {
  const onFieldChange = value => {
    let dateValue = value;

    // if the date field isn't in a valid date format,
    // react-datetime's onChange handler returns a string
    // otherwise it returns a moment object
    // this is why we can't override DateTime's onChange
    // prop with Formik's field.onChange
    if (value instanceof moment) {
      dateValue = moment(value).format(DATE_FORMAT);
    }

    form.setFieldValue(field.name, dateValue);
  }

  const onFieldBlur = () => {
    form.setFieldTouched(field.name, true);
  }

  return (
    <Datetime
      dateFormat={DATE_FORMAT}
      timeFormat={timeFormat}
      id={field.name}
      name={field.name}
      onChange={onFieldChange}
      onBlur={onFieldBlur}
    />
  );
}

export default FormikDateTime;