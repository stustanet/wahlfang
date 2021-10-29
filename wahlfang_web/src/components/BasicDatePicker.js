import * as React from 'react';
import TextField from '@mui/material/TextField';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DateTimePicker from '@mui/lab/DateTimePicker';

export default function BasicDatePicker({
    form: {setFieldValue},
    field: {name, value},
    ...rest

    }) {
    const [date, setDate] = React.useState(new Date());
    // start_date -> Start date (Optional)
    let label = name.replace('_', ' ')
    label = label.charAt(0).toUpperCase() + label.slice(1)
    label = label + ' (Optional)'
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <DateTimePicker
          label={label}
          clearable
          autoOk
          disablePast
          value={value}
          onChange={(newValue) => {
                setFieldValue(name, newValue);
            }}
          id={name}
          renderInput={(params) => <TextField
              {...params}
              style = {{width: '100%'}}
              variant="standard"
              error={false}
          />}
        />
    </LocalizationProvider>
  );
}