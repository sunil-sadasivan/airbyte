import { FieldProps } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LabeledRadioButton, Link } from "components";

import { useConfig } from "config";
import { NormalizationType } from "core/domain/connection/operation";

import { ConnectionFormMode } from "../ConnectionForm";

const Normalization = styled.div`
  margin: 16px 0;
`;

type NormalizationBlockProps = FieldProps<string> & {
  mode: ConnectionFormMode;
};

const NormalizationField: React.FC<NormalizationBlockProps> = ({ form, field, mode }) => {
  const config = useConfig();
  return (
    <Normalization>
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.raw"
        label={<FormattedMessage id="form.rawData" />}
        value={NormalizationType.RAW}
        checked={field.value === NormalizationType.RAW}
        disabled={mode === "readonly"}
      />
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.basic"
        label={<FormattedMessage id="form.basicNormalization" />}
        value={NormalizationType.BASIC}
        checked={field.value === NormalizationType.BASIC}
        disabled={mode === "readonly"}
        message={
          mode !== "readonly" && (
            <FormattedMessage
              id="form.basicNormalization.message"
              values={{
                lnk: (lnk: React.ReactNode) => (
                  <Link target="_blank" href={config.ui.normalizationLink} as="a">
                    {lnk}
                  </Link>
                ),
              }}
            />
          )
        }
      />
    </Normalization>
  );
};

export { NormalizationField };
