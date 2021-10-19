import * as React from 'react';
import TextField from '@mui/material/TextField';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DateTimePicker from '@mui/lab/DateTimePicker';

export default function BasicDatePicker({
    name,
    form: {setFieldValue},
    field: {value},
    ...rest

    }) {
  const [date, setDate] = React.useState(new Date());
  console.log()
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <DateTimePicker
          label="Meeting start (optional)"
          clearable
          autoOk
          disablePast
          value={value}
          onChange={(newValue) => {
                setFieldValue("start_date", newValue);
            }}
          id="start_date"
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