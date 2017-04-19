import React, {Component} from "react";
import {ListGroupItem} from "react-bootstrap";
import Moment from "moment";
import Filesize from "filesize";
import {Link} from "react-router";
import ActionIcon from "./ActionIcon";


export default class BoxProviderList extends Component {
  renderDeleteIcon = (provider) => {
    if (!this.props.canDelete) {
      return null;
    }
    return <ActionIcon
        icon="trash"
        title="Delete provider"
        onClick={this.props.onDelete.bind(null, provider.provider)}
    />;
  };

  renderEditIcon = (provider) => {
    if (!this.props.canEdit) {
      return null;
    }
    return <ActionIcon
        icon="edit"
        title="Edit provider"
        onClick={this.props.onEdit.bind(null, provider.provider)}
    />;
  };

  renderDownloadButton = (provider) => {
    if (!provider.download_url) {
      return <p>No box file</p>;
    }
    return (
        <a href={provider.download_url} className="btn btn-default">
          Download box
        </a>
    );
  };

  renderSize = (provider) => {
    if (!provider.download_url) {
      return null;
    }
    return (
        <p>Size: {Filesize(provider.file_size)}</p>
    );
  };

  renderProvidersList = () => {
    if (!this.props.providers) {
      return null;
    }

    if (!this.props.providers.length) {
      return <p className="text-center">No providers</p>;
    }

    return this.props.providers.map(provider => {
      return (
          <ListGroupItem
              key={provider.tag}
          >
            <h4 className="list-group-item-heading">
              {provider.provider} |&nbsp;
              <small title={Moment(provider.date_updated).format('LLL')}>
                Last updated: {Moment(provider.date_updated).fromNow()}
              </small>
              <div className="pull-right">
                {this.renderEditIcon(provider)}
                {this.renderDeleteIcon(provider)}
              </div>
            </h4>
            {this.renderSize(provider)}
            {this.renderDownloadButton(provider)}
          </ListGroupItem>
      );
    });
  };

  renderNewButton = () => {
    if (!this.props.canCreate) {
      return null;
    }
    return (
        <Link
            to={`/boxes/${this.props.boxTag}/versions/${this.props.version}/providers/new/`}
            className='btn btn-success box-provider-new-button'
        >
          New provider
        </Link>
    );
  };

  render() {
    return (
      <div>
        {this.renderNewButton()}
        {this.renderProvidersList()}
      </div>
    );
  }
}
